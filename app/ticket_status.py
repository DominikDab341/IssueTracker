from enum import StrEnum


class TicketStatus(StrEnum):
    REPORTED = "reported"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


ACTIVE_STATUSES = (TicketStatus.REPORTED, TicketStatus.ACCEPTED, TicketStatus.IN_PROGRESS)
TERMINAL_STATUSES = (TicketStatus.RESOLVED, TicketStatus.REJECTED, TicketStatus.CANCELLED)
ALLOWED_TRANSITIONS = {
    TicketStatus.REPORTED: {TicketStatus.ACCEPTED, TicketStatus.REJECTED, TicketStatus.CANCELLED},
    TicketStatus.ACCEPTED: {TicketStatus.IN_PROGRESS, TicketStatus.REJECTED},
    TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED, TicketStatus.REJECTED},
    TicketStatus.RESOLVED: set(),
    TicketStatus.REJECTED: set(),
    TicketStatus.CANCELLED: set(),
}


MAX_STATUS_NOTE_LENGTH = 2000


def normalize_status_note(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) > MAX_STATUS_NOTE_LENGTH:
        raise ValueError(f"Notatka może mieć najwyżej {MAX_STATUS_NOTE_LENGTH} znaków.")
    value = value.strip()
    if not value:
        raise ValueError("Notatka nie może być pusta.")
    return value


def validate_status_notes(status: TicketStatus, resolution_note: str | None,
                          rejection_reason: str | None) -> None:
    if status == TicketStatus.RESOLVED and not resolution_note:
        raise ValueError("Rozwiązanie zgłoszenia wymaga opisu rozwiązania.")
    if status == TicketStatus.REJECTED and not rejection_reason:
        raise ValueError("Odrzucenie zgłoszenia wymaga powodu odrzucenia.")
    if resolution_note is not None and status != TicketStatus.RESOLVED:
        raise ValueError("Opis rozwiązania można zapisać tylko przy rozwiązaniu zgłoszenia.")
    if rejection_reason is not None and status != TicketStatus.REJECTED:
        raise ValueError("Powód odrzucenia można zapisać tylko przy odrzuceniu zgłoszenia.")
