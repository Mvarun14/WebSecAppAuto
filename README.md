WebSecAppAuto


This project demonstrates common web vulns (SQLi, Stored XSS, CSRF, Path Traversal, IDOR) and secure fixes.



python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python init_dbs.py


python -m vulnerable_app.app   
python -m secure_app.app       


python auto_exploit.py


pytest -q

