"""
    Logic conditions base class
"""
from typing import List

from pydantic import Field, validator

from ..base import ConditionBase, ABCMeta


class LogicCondition(ConditionBase, metaclass=ABCMeta):
    """
    Base class for logical conditions
    """

    values: List = Field(min_items=1)

    def is_satisfied(self, ctx) -> bool:
        raise NotImplementedError()

    @validator("values", each_item=True)
    def list_of_obj(cls, v):
        if v is None:
            raise TypeError("item type of values cannot be None")
        return v
