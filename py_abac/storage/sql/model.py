"""
    SQL storage policy model
"""

from typing import Union, List, Type

from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy import literal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column, Mapped

from ..._policy import Policy

Base = declarative_base()


class TargetModel:
    """
    Base policy target model
    """

    target_id: Mapped[str] = mapped_column(String(248), comment="Target ID used for filtering policies")


class SubjectTargetModel(TargetModel, Base):
    """
    Subject target data model
    """

    __tablename__ = "py_abac_subject_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(248), ForeignKey("py_abac_policies.uid", ondelete="CASCADE"))


class ResourceTargetModel(TargetModel, Base):
    """
    Resource target data model
    """

    __tablename__ = "py_abac_resource_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(248), ForeignKey("py_abac_policies.uid", ondelete="CASCADE"))


class ActionTargetModel(TargetModel, Base):
    """
    Action target data model
    """

    __tablename__ = "py_abac_action_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(248), ForeignKey("py_abac_policies.uid", ondelete="CASCADE"))


class PolicyModel(Base):
    """
    Policy data model
    """

    __tablename__ = "py_abac_policies"

    uid: Mapped[str] = mapped_column(String(248), primary_key=True)
    json: Mapped[dict] = mapped_column(JSON(), nullable=False)
    subjects = relationship(SubjectTargetModel, passive_deletes=True, lazy="joined")
    resources = relationship(ResourceTargetModel, passive_deletes=True, lazy="joined")
    actions = relationship(ActionTargetModel, passive_deletes=True, lazy="joined")

    @classmethod
    def from_policy(cls, policy: Policy) -> "PolicyModel":
        """
        Create `PolicyModel` from `Policy` object
        """
        rvalue = cls()
        rvalue._setup(policy)  # pylint: disable=protected-access

        return rvalue

    def to_policy(self) -> Policy:
        """
        Get `Policy` object from model instance
        """
        return Policy.from_json(self.json)

    def update(self, policy: Policy):
        """
        Update policy model instance to match policy object
        """
        self._setup(policy)

    @classmethod
    def get_filter(cls, subject_id: str, resource_id: str, action_id: str):
        """
        Get query filter for policies matching target IDs
        """
        return [
            cls.subjects.any(literal(subject_id).op("LIKE", is_comparison=True)(SubjectTargetModel.target_id)),
            cls.resources.any(literal(resource_id).op("LIKE", is_comparison=True)(ResourceTargetModel.target_id)),
            cls.actions.any(literal(action_id).op("LIKE", is_comparison=True)(ActionTargetModel.target_id)),
        ]

    def _setup(self, policy: Policy):
        """
        Setup instance using policy object
        """
        self.uid = policy.uid
        self.json = policy.to_json()

        # Setup targets
        self._setup_targets(policy.targets.subject_id, self.subjects, SubjectTargetModel, policy.uid)
        self._setup_targets(policy.targets.resource_id, self.resources, ResourceTargetModel, policy.uid)
        self._setup_targets(policy.targets.action_id, self.actions, ActionTargetModel, policy.uid)

    @staticmethod
    def _setup_targets(
        target_id: Union[str, List[str]], model_attr: List[TargetModel], target_model_cls: Type[TargetModel], uid: str
    ):
        """
        Setup policy target ID(s) into model attribute.
        """
        # Create list of target ID(s) present in policy
        target_ids = target_id if isinstance(target_id, list) else [target_id]
        old_target_ids = tuple(x.target_id.replace("%", "*") for x in model_attr)
        new_target_ids = (x for x in target_ids if x not in old_target_ids)
        # Add new targets in policy model
        for tid in new_target_ids:
            target_model = target_model_cls()
            # Replace with SQL wildcard '%'
            target_model.uid = uid
            target_model.target_id = tid.replace("*", "%")
            model_attr.append(target_model)
        # remove policy not exist any more
        for k, v in enumerate(model_attr):
            if v.target_id.replace("%", "*") not in target_ids:
                model_attr.pop(k)
