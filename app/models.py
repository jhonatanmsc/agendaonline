import json
from datetime import date

from mongoengine import Document, StringField, DateField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField, BooleanField

from app.enums import CATEGORIES
from app.settings import pwd_context
from app.utils.date_parse import datetime_to_str


class Users(Document):
    name = StringField(max_length=150)
    email = StringField(unique=True, required=True)
    hashed_password = StringField(required=True)
    cellphone = StringField(max_length=50)
    category = StringField(choices=CATEGORIES)
    is_active = BooleanField(default=True)
    created_at = DateField(default=date.today())

    def __init__(self, *args, **values):
        if values.get('password'):
            values['hashed_password'] = pwd_context.hash(values['password'])
            values.pop('password')
        super().__init__(*args, **values)

    def set_password(self, pwd):
        self.hashed_password = pwd_context.hash(pwd)
        self.save()

    def verify_password(self, pwd):
        return pwd_context.verify(pwd, self.hashed_password)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        registro["created_at"] = datetime_to_str(registro["created_at"]["$date"])
        return registro


class Contacts(Document):
    name = StringField(max_length=150)
    cellphone = StringField(max_length=50)
    category = StringField(choices=CATEGORIES)
    created_at = DateField(default=date.today())

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        registro["created_at"] = datetime_to_str(registro["created_at"]["$date"])
        return registro


class ContactsEmb(EmbeddedDocument):
    id = StringField(max_length=100)
    name = StringField(max_length=150)
    cellphone = StringField(max_length=50)
    category = StringField(choices=CATEGORIES)
    is_present = BooleanField(default=False)


class Registries(Document):
    created_at = DateField(default=date.today())
    contacts = ListField(EmbeddedDocumentField(ContactsEmb))
    category = StringField(choices=CATEGORIES)
    is_active = BooleanField(default=True)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        registro["created_at"] = datetime_to_str(registro["created_at"]["$date"])
        return registro
