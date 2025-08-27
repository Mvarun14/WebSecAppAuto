from vulnerable_app.app import app as vapp
from secure_app.app import app as sapp

def login(client, username='alice', password='password123'):
    return client.post('/login', data={'username': username, 'password': password})

def test_vuln_idor_account_view():
    c = vapp.test_client()
    login(c, 'alice', 'password123')
    r = c.get('/account?user_id=2')
    assert b"Account for bob" in r.data

def test_vuln_idor_transfer():
    c = vapp.test_client()
    login(c, 'alice', 'password123')
    r = c.post('/transfer', data={'from_user_id': 2, 'to_user_id': 1, 'amount': 10})
    assert r.status_code == 200

def test_secure_idor_blocked_view():
    c = sapp.test_client()
    login(c, 'alice', 'password123')
    r = c.get('/account?user_id=2')
    assert b"bob" not in r.data 

def test_secure_idor_blocked_transfer():
    c = sapp.test_client()
    login(c, 'alice', 'password123')
    r = c.post('/transfer', data={'to_user_id': 2, 'amount': 10})
    assert r.status_code == 200  
