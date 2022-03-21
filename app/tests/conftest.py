import pytest
import sys
import os

from starlette.testclient import TestClient

sys.path.append(__package__)
os.environ['TEST_MODE'] = 'true'

from main import app
from app.models import Users


@pytest.fixture(scope="module")
def admin_user():
    user = Users(
        name="usuario de teste",
        email="teste@mail.com",
        category="CRIANÇAS",
        cellphone="86988969872",
        password="123456"
    ).save()
    return user


@pytest.fixture(scope="module")
def api():
    return TestClient(app)


@pytest.fixture(scope='module')
def auth_api(api, admin_user):
    res = api.post('/login', json={"email": admin_user.email, "password": "a123456"})
    api.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {res.json["access_token"]}'
    return api
