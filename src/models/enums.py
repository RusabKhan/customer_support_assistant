from enum import Enum


class Role(str, Enum):
    """
Enumeration of user roles within the system.

Defines possible roles: user, admin, and support.
"""
    user = "user"
    admin = "admin"
    support = "support"

class TicketStatus(str, Enum):
    """
Enumeration of possible statuses for a ticket, including open, closed, in progress, on hold, and resolved.
"""
    open = "open"
    closed = "closed"
    in_progress = "in_progress"
    on_hold = "on_hold"
    resolved = "resolved"

class Permission(str, Enum):
    """
Enumeration of user permissions for authentication and ticket management actions.
"""
    CREATE_USER = "create_user"
    LOGIN = "login"
    VIEW_ALL_TICKETS = "view_all_tickets"
    VIEW_OWN_TICKETS = "view_own_tickets"
    CREATE_TICKET = "create_ticket"
    GROQ_ASSISTANT = "groq_assistant"


RolePermissions = {
    Role.admin: {
        Permission.CREATE_USER,
        Permission.LOGIN,
        Permission.VIEW_ALL_TICKETS,
        Permission.CREATE_TICKET,
        Permission.GROQ_ASSISTANT
    },
    Role.user: {
        Permission.LOGIN,
        Permission.VIEW_OWN_TICKETS,
        Permission.CREATE_TICKET,
    },
    Role.support: {
        Permission.LOGIN,
        Permission.VIEW_ALL_TICKETS,
    },
}

