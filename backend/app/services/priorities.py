from dataclasses import dataclass

from app.domain import PRIORITIES, Priority, PrioritySource


@dataclass(frozen=True)
class PriorityDecision:
    priority: Priority
    source: PrioritySource


def determine_priority(*, manual_priority: str | None, work_blocked: bool,
                       automatic_priority: str | None) -> PriorityDecision:
    """Wyznacza decyzję bez zmiany obiektu zgłoszenia i bez efektów ubocznych."""
    if manual_priority in PRIORITIES:
        return PriorityDecision(Priority(manual_priority), PrioritySource.ADMINISTRATOR)
    if work_blocked:
        return PriorityDecision(Priority.CRITICAL, PrioritySource.WORK_BLOCKED)
    if automatic_priority in PRIORITIES:
        return PriorityDecision(Priority(automatic_priority), PrioritySource.AUTOMATIC)
    return PriorityDecision(Priority.MEDIUM, PrioritySource.FALLBACK)


def update_effective_priority(ticket):
    decision = determine_priority(manual_priority=ticket.manual_priority,
                                  work_blocked=ticket.work_blocked,
                                  automatic_priority=ticket.automatic_priority)
    ticket.priority, ticket.priority_source = decision.priority, decision.source
