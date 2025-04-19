from enum import Enum


class Role(str, Enum):
    user = "user"
    admin = "admin"
    support = "support"


class Permission(str, Enum):
    CREATE_USER = "create_user"
    LOGIN = "login"
    VIEW_ALL_TICKETS = "view_all_tickets"
    VIEW_OWN_TICKETS = "view_own_tickets"
    CREATE_TICKET = "create_ticket"


RolePermissions = {
    Role.admin: {
        Permission.CREATE_USER,
        Permission.LOGIN,
        Permission.VIEW_ALL_TICKETS,
        Permission.CREATE_TICKET,
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

