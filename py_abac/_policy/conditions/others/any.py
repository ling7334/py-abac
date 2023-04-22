"""
    Attribute any value conditions
"""
from ..base import ConditionBase


class Any(ConditionBase):
    """
        Condition for attribute having any value
    """
    # Condition type specifier
    condition: str = "Any"

    def is_satisfied(self, ctx) -> bool:
        return True
