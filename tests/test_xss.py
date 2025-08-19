from vulnerable_app.app import app as vapp
from secure_app.app import app as sapp

def test_vuln_stored_xss_reflected():
    c = vapp.test_client()
    c.post('/comments', data={'username':'attacker','comment':'<script>alert(1)</script>'})
    resp = c.get('/comments')
    assert b"<script>alert(1)</script>" in resp.data

def test_secure_stored_xss_sanitized():
    c = sapp.test_client()
    c.post('/comments', data={'username':'attacker','comment':'<script>alert(1)</script>'})
    resp = c.get('/comments')
    assert b"<script>alert(1)</script>" not in resp.data
