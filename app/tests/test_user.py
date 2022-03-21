import json
import pdb


def test_login(api, admin_user):
    payload = {
        "email": admin_user.email,
        "password": "123456"
    }
    res = api.post('/login', data=json.dumps(payload))

    assert res.status_code == 200
