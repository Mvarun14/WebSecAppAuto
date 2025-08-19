# WebAppSecLab (Flask) — Vulnerable vs Secure + Auto-Exploit + IDOR

This lab demonstrates common web vulns (SQLi, Stored XSS, CSRF, Path Traversal, **IDOR**) and secure fixes.

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python init_dbs.py

# Run apps (two terminals)
python -m vulnerable_app.app   # http://127.0.0.1:5001
python -m secure_app.app       # http://127.0.0.1:5002

# Auto exploit demo (third terminal)
python auto_exploit.py

# Tests
pytest -q
```
