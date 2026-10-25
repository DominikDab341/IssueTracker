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
