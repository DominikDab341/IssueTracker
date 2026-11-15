import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Category
from app.models.models import Ticket, User
from app.services.access import available_tickets
from app.services.tasks import now


REPORTING_ZONE = ZoneInfo("Europe/Warsaw")
CATEGORIES = {
    Category.ACCOUNTS_ACCESS: ("Accounts and access", r"accounts?|access|permissions?"),
    Category.HARDWARE: ("Hardware", r"hardware|equipment"),
    Category.NETWORK: ("Network and connectivity", r"networks?|networking|connectivity"),
    Category.SOFTWARE: ("Software", r"software|applications?"),
    "unknown": ("Needs review", r"unclassified|unknown|needs review"),
}
GUIDANCE = ("I can count tickets and compare category volumes using creation dates. "
            "Try “Which category had the most tickets last month?” or "
            "“Did network issues increase compared with the previous month?”")
_SUBJECT = r"\b(tickets?|categories|category|issues?|problems?|reports?|cases?|incidents?)\b"
_COUNT = r"\b(how many|count|number of|total|most|top|rank(?:ing)?|breakdown|volume|distribution|statistics)\b"
_COMPARE = r"\b(compare\w*|versus|vs|trend\w*|increas\w*|decreas\w*|grow\w*|grew|ris(?:e|ing)|rose|fall\w*|fell|drop(?:ped)?|more|fewer)\b"
_PERIOD = re.compile(r"\b(?:(this|last|previous|current) (month|week)|(?:last|past) (\d{1,3}) days?|all[ -]time)\b")
_OTHER_TIME = (r"\b(?:today|yesterday|tomorrow|next|since|between|until|from|ago|year|years|quarter|"
               r"months|weeks|days?|week|month|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
               r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b"
               r"|\b\d{4}\b")
_UNSUPPORTED = (r"\b(?:resolved|closed|cancelled|rejected|open|active|pending|unresolved|priority|severity|"
                r"assignee|reporter|authors?|users?|average|median|resolution time|how long|recurr\w*|"
                r"repeat\w*|each day|each week|each month|by day|by week|by month|by team|by status)\b")
_UNSUPPORTED_SUBJECT = (r"\b(?:vpn|wi-fi|wifi|printers?|outlook|mfa|passwords?|logins?|emails?|teams|docks?|"
                        r"usb|disconnect\w*|mention\w*|contain\w*|related to|about)\b")


@dataclass(frozen=True)
class Period:
    start: date | None
    end: date

    def label(self) -> str:
        last_day = self.end - timedelta(days=1)
        if self.start is None:
            return f"All time through {last_day.isoformat()}"
        return f"{self.start.isoformat()} to {last_day.isoformat()}"


@dataclass(frozen=True)
class StatisticsRequest:
    period: Period
    previous: Period | None = None
    category: str | None = None
    by_category: bool = False


def _periods(unit: str, current: bool, days: str | None, today: date) -> tuple[Period, Period]:
    if days or unit == "week":
        span = timedelta(days=int(days or 7))
        boundary = today - timedelta(days=today.weekday()) if not days else today
        start = boundary if current else boundary - span
        return Period(start, today + timedelta(days=1) if current else boundary), Period(start - span, start)
    boundary = today.replace(day=1)
    last_month = (boundary - timedelta(days=1)).replace(day=1)
    start = boundary if current else last_month
    return (Period(start, today + timedelta(days=1) if current else boundary),
            Period((start - timedelta(days=1)).replace(day=1), start))


def parse_statistics(question: str, today: date) -> StatisticsRequest | str | None:
    query = question.casefold()
    categories = [key for key, (_, alias) in CATEGORIES.items() if re.search(rf"\b(?:{alias})\b", query)]
    ranking = bool(re.search(
        r"\b(?:which|what) (?:\w+ ){0,4}(?:most|top)\b|"
        r"\b(?:by category|breakdown|rank(?:ing)?|distribution|top categories)\b", query))
    compare = bool(re.search(_COMPARE, query))
    count = bool(re.search(_COUNT, query)) or ranking
    subject = re.search(_SUBJECT, query)
    if not ((count and subject) or (compare and (subject or categories))):
        return None
    # "How many times should I retry?" and "What is the most common fix?" are ticket questions.
    if re.search(r"\b(?:fix(?:es)?|solutions?|workarounds?|steps)\b", query):
        return None
    matches = list(_PERIOD.finditer(query))
    ranking |= bool(re.search(r"\bmost (?:common|frequent) (?:tickets?|issues?|problems?|reports?|cases?)\b", query))
    if (re.search(_UNSUPPORTED, query) or re.search(_UNSUPPORTED_SUBJECT, query) or len(categories) > 1
            or re.search(_OTHER_TIME, _PERIOD.sub("", query))
            or any(match[3] and not 1 <= int(match[3]) <= 365 for match in matches)):
        return GUIDANCE
    if any(match[2] is None and match[3] is None for match in matches):
        if compare or len(matches) != 1:
            return GUIDANCE
        return StatisticsRequest(Period(None, today + timedelta(days=1)),
                                 category=next(iter(categories), None), by_category=ranking)
    if len(matches) > 2 or (len(matches) == 2 and (
        not compare or matches[0][3] or matches[1][3] or matches[0][2] != matches[1][2]
        or {match[1] in {"this", "current"} for match in matches} != {True, False}
    )):
        return GUIDANCE
    unit = matches[0][2] if matches else "month"
    days = matches[0][3] if matches else None
    current = any(match[1] in {"this", "current"} for match in matches)
    period, previous = _periods(unit, current, days, today)
    if not compare and not matches:
        period = Period(None, today + timedelta(days=1))
    by_category = ranking or bool(compare and re.search(r"\b(?:which|what) (?:ticket )?categor", query))
    return StatisticsRequest(period, previous if compare else None, next(iter(categories), None), by_category)


def _scope(period: Period):
    end = Ticket.created_at < datetime.combine(period.end, time.min, REPORTING_ZONE)
    if period.start is None:
        return end
    return end & (Ticket.created_at >= datetime.combine(period.start, time.min, REPORTING_ZONE))


def _change(current: int, previous: int) -> str:
    if previous == 0 and current:
        percent = "percentage unavailable because the earlier count was zero"
    else:
        percent = f"{(current - previous) / previous:+.1%}" if previous else "0.0%"
    return f"{current} vs {previous} ({current - previous:+d}, {percent})"


async def answer_statistics(db: AsyncSession, actor: User, question: str) -> str | None:
    today = now().astimezone(REPORTING_ZONE).date()
    request = parse_statistics(question, today)
    if request is None or isinstance(request, str):
        return request
    # Both periods are read by the same statement. Counts include tickets in any status.
    current = _scope(request.period)
    previous = _scope(request.previous) if request.previous else False
    statement = select(
        Ticket.category,
        func.count().filter(current),
        func.count().filter(previous),
    ).where(available_tickets(actor), current | previous).group_by(Ticket.category)
    if request.category is not None:
        statement = statement.where(Ticket.category == request.category)
    counts = {category: (count, earlier) for category, count, earlier in await db.execute(statement)}
    heading = request.period.label()
    label = CATEGORIES[request.category][0] if request.category is not None else "All tickets"
    total = sum(count for count, _ in counts.values())
    if request.previous:
        heading += f" compared with {request.previous.label()}"
        if request.period.end > today:
            heading += " · current period to date"
        earlier_total = sum(earlier for _, earlier in counts.values())
        lines = [f"{label}: {_change(total, earlier_total)}"]
        if request.by_category and request.category is None:
            for category, (count, earlier) in sorted(counts.items(), key=lambda row: (row[1][1] - row[1][0], row[0])):
                lines.append(f"{CATEGORIES.get(category, (category,))[0]}: {_change(count, earlier)}")
    else:
        lines = [f"{label}: {total}"]
        if request.by_category and request.category is None:
            for category, (count, _) in sorted(counts.items(), key=lambda row: (-row[1][0], row[0])):
                lines.append(f"{CATEGORIES.get(category, (category,))[0]}: {count}")
    return f"Tickets created · {heading} ({REPORTING_ZONE.key})\n" + "\n".join(lines)
