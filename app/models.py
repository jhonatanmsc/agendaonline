import json

from mongoengine import Document, StringField, DateField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField, BooleanField
from werkzeug.security import generate_password_hash, check_password_hash

from app.enums import CATEGORIES
from app.settings import pwd_context


class Users(Document):
    name = StringField(max_length=150)
    email = StringField(required=True)
    hashed_password = StringField(required=True)
    cellphone = StringField(max_length=50)
    category = StringField(choices=CATEGORIES)

    def __init__(self, *args, **values):
        if values.get('password'):
            values['hashed_password'] = pwd_context.hash(values['password'])
            values.pop('password')
        super().__init__(*args, **values)

    def verify_password(self, pwd):
        return pwd_context.verify(pwd, self.hashed_password)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        return registro


class Contacts(Document):
    name = StringField(max_length=150)
    cellphone = StringField(max_length=50)
    category = StringField(choices=CATEGORIES)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        return registro


class ContactsEmb(EmbeddedDocument):
    name = StringField(max_length=150)
    cellphone = StringField(max_length=50)
    present = BooleanField(default=False)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        return registro


class Registries(Document):
    created_at = DateField()
    contacts = ListField(EmbeddedDocumentField(ContactsEmb))
    category = StringField(choices=CATEGORIES)

    def as_dict(self):
        registro = json.loads(self.to_json())
        registro["id"] = str(registro.pop("_id")["$oid"])
        return registro
