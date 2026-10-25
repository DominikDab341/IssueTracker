PRIORITIES = {"low", "medium", "high", "critical"}


def update_effective_priority(ticket):
    if ticket.manual_priority in PRIORITIES:
        ticket.priority, ticket.priority_source = ticket.manual_priority, "administrator"
    elif ticket.work_blocked:
        ticket.priority, ticket.priority_source = "critical", "work_blocked"
    elif ticket.automatic_priority in PRIORITIES:
        ticket.priority, ticket.priority_source = ticket.automatic_priority, "automatic"
    else:
        ticket.priority, ticket.priority_source = "medium", "fallback"
