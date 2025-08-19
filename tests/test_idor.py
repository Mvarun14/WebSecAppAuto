from vulnerable_app.app import app as vapp
from secure_app.app import app as sapp

def login(client, username='alice', password='password123'):
    return client.post('/login', data={'username': username, 'password': password})

def test_vuln_idor_account_view():
    c = vapp.test_client()
    login(c, 'alice', 'password123')
    # Alice reading Bob's account by changing user_id
    r = c.get('/account?user_id=2')
    assert b"Account for bob" in r.data

def test_vuln_idor_transfer():
    c = vapp.test_client()
    login(c, 'alice', 'password123')
    # Move money from Bob to Alice by forging from_user_id
    r = c.post('/transfer', data={'from_user_id': 2, 'to_user_id': 1, 'amount': 10})
    assert r.status_code == 200

def test_secure_idor_blocked_view():
    c = sapp.test_client()
    login(c, 'alice', 'password123')
    # Secure app ignores user_id param; only serves own account
    r = c.get('/account?user_id=2')
    assert b"bob" not in r.data  # should show only alice's account

def test_secure_idor_blocked_transfer():
    c = sapp.test_client()
    login(c, 'alice', 'password123')
    # Cannot transfer from someone else's account; secure app uses session as source
    r = c.post('/transfer', data={'to_user_id': 2, 'amount': 10})
    assert r.status_code == 200  # success path uses alice as source only
