from vulnerable_app.app import app as vapp
from secure_app.app import app as sapp

def test_vuln_sqli_login_bypass():
    c = vapp.test_client()
    resp = c.post('/login', data={'username': "alice", 'password': "' OR '1'='1"})
    assert b"Welcome" in resp.data

def test_secure_sqli_prevented():
    c = sapp.test_client()
    resp = c.post('/login', data={'username': "alice", 'password': "' OR '1'='1"})
    assert b"Welcome" not in resp.data
