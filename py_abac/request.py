"""
    Authorization request class
"""

from typing import Optional

from pydantic import BaseModel, Field, StrictStr, DictError, validator

from .exceptions import RequestCreateError


class AccessRequest(BaseModel):
    """
    Authorization request sent by PEP

    :Example:

    .. code-block:: python

        # Create a access request JSON from flask request object
        request_json = {
            "subject": {
                "id": "",
                "attributes": {"name": request.values.get("username")}
            },
            "resource": {
                "id": "",
                "attributes": {"name": request.path}
            },
            "action": {
                "id": "",
                "attributes": {"method": request.method}
            },
            "context": {}
        }
        # Parse JSON and create access request object
        request = AccessRequest.from_json(request_json)
    """

    subject_id: StrictStr = Field(max_length=400)
    subject: dict = Field(default_factory=dict)
    resource_id: StrictStr = Field(max_length=400)
    resource: dict = Field(default_factory=dict)
    action_id: StrictStr = Field(max_length=400)
    action: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)

    def __init__(self, subject: dict, resource: dict, action: dict, context: Optional[dict] = None):
        assert isinstance(subject.get("attributes"), dict) or subject.get("attributes") is None
        # assert isinstance(resource.get("attributes"), dict) or resource.get("attributes") is None
        # assert isinstance(action.get("attributes"), dict) or action.get("attributes") is None
        super().__init__(
            subject_id=subject.get("id"),
            subject=subject.get("attributes", {}),
            resource_id=resource.get("id"),
            resource=resource.get("attributes", {}),
            action_id=action.get("id"),
            action=action.get("attributes", {}),
            context=context or {},
        )

    @staticmethod
    def from_json(data: dict) -> "AccessRequest":
        """
        Create access request object from JSON
        """
        try:
            return AccessRequest(**data)
        except Exception as err:
            raise RequestCreateError(*err.args)


# backward compatible with v0.2.0
Request = AccessRequest


# class _AccessElementSchema(Schema):
#     """
#         JSON schema for access element
#     """
#     id = fields.String(required=True, validate=validate.Length(max=400))
#     attributes = fields.Dict(default={}, missing={})


# class _RequestSchema(Schema):
#     """
#             JSON schema for authorization request
#         """
#     subject = fields.Nested(_AccessElementSchema, required=True)
#     resource = fields.Nested(_AccessElementSchema, required=True)
#     action = fields.Nested(_AccessElementSchema, required=True)
#     context = fields.Dict(default={}, missing={})

#     @post_load
#     def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
#         return AccessRequest(**data)
