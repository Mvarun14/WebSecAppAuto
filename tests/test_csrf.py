from secure_app.app import app as sapp
from vulnerable_app.app import app as vapp

def test_vulnerable_no_csrf_allows_post():
    c = vapp.test_client()
    r = c.post('/comments', data={'username':'x','comment':'y'}, follow_redirects=True)
    assert r.status_code == 200

def test_secure_requires_csrf():
    c = sapp.test_client()
    r = c.post('/comments', data={'username':'x','comment':'y'}, follow_redirects=True)
    assert r.status_code in (400, 403)
