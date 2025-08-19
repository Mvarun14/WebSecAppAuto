from vulnerable_app.app import app as vapp
from secure_app.app import app as sapp

def test_vuln_path_traversal_reads_parent():
    c = vapp.test_client()
    r = c.get('/download?file=../vuln.db')
    assert r.status_code != 404

def test_secure_prevent_path_traversal():
    c = sapp.test_client()
    r = c.get('/download?file=../secure.db')
    assert r.status_code == 404
