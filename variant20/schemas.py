from marshmallow import Schema, fields, post_load, validate
from marshmallow_enum import EnumField
from .database import User, Advertisement, ModifierEnum, RoleEnum


class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=30))
    email = fields.Email(required=True)
    password_hash = fields.String(required=True, validate=validate.Length(max=512))
    role = EnumField(RoleEnum, default=RoleEnum.average, missing='average')

    @post_load
    def create_user(self, data, **kwargs):
        return User(**data)


class AdvertisementSchema(Schema):
    id = fields.Integer()
    summary = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(validate=validate.Length(max=256))
    topic = fields.String(required=True, validate=validate.Length(max=15))
    modifier = EnumField(ModifierEnum)
    user_id = fields.Integer()

    @post_load
    def create_advertisement(self, data, **kwargs):
        return Advertisement(**data)
