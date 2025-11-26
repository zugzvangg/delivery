from enum import Enum


class NotCreatedOrderStatus(Exception):
    pass


class NotAssignedOrderStatus(Exception):
    pass


class NotCompletedOrderStatus(Exception):
    pass


class OrderStatus(Enum):
    CREATED: str = "CREATED"
    ASSIGNED: str = "ASSIGNED"
    COMPLETED: str = "COMPLETED"
