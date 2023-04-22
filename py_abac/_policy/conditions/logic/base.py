"""
    Logic conditions base class
"""
from typing import List

from pydantic import Field

from ..base import ConditionBase, ABCMeta


class LogicCondition(ConditionBase, metaclass=ABCMeta):
    """
    Base class for logical conditions
    """

    values: List = Field(min_items=1)

    def is_satisfied(self, ctx) -> bool:
        raise NotImplementedError()
