"""
    Policy class
"""

from .rules import Rules
from .targets import Targets
from ..context import EvaluationContext
from ..exceptions import PolicyCreateError

from pydantic import BaseModel, Field, ValidationError


class Access(str):
    """
    Access decisions
    """

    DENY_ACCESS = "deny"
    ALLOW_ACCESS = "allow"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v in ["deny", "allow"]:
            return v
        raise ValidationError(*KeyError("Only `deny` and `allow` is valid").args)


class Policy(BaseModel):
    """
    Policy class containing rules and targets
    """

    uid: str
    description: str = ""
    rules: Rules
    targets: Targets
    effect: Access
    priority: int = Field(default=0, ge=0)

    @classmethod
    def from_json(cls, data: dict | str) -> "Policy":
        """
        Create Policy object from JSON
        """
        try:
            if isinstance(data, dict):
                return cls.parse_obj(data)
            return cls.parse_raw(data)
        except ValidationError as err:
            raise PolicyCreateError(err.json())

    def to_json(self):
        """
        Convert policy object to JSON
        """
        return self.dict()

    def fits(self, ctx: EvaluationContext) -> bool:
        """
        Check if the request fits policy

        :param ctx: evaluation context
        :return: True if fits else False
        """
        return self.rules.is_satisfied(ctx) and self.targets.match(ctx)

    @property
    def is_allowed(self) -> bool:
        """
        Check if access is allowed
        """
        return self.effect == Access.ALLOW_ACCESS
