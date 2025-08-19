from vulnerable_app.app import init_db as init_vuln_db, app as vuln_app
from secure_app.app import init_db as init_sec_db, app as sec_app

with vuln_app.app_context():
    init_vuln_db()

with sec_app.app_context():
    init_sec_db()

print("Databases initialized")
