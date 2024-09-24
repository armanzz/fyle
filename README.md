

## Installation

1. Fork this repository to your github account
2. Clone the forked repository and proceed with steps mentioned below

### Install requirements

```

python -m venv venv
./venv/scripts/activate
pip install -r requirements.txt
```
### Reset DB

```

$env:FLASK_APP="core/server.py"
Remove-Item -Path "instance/store.sqlite3"
flask db upgrade -d core/migrations/
```
### Start Server

```
flask run
```
### Run Tests

```
pytest -vvv -s tests/

# for test coverage report
# pytest --cov
# open htmlcov/index.html
```

### Coverage Report:


![Screenshot (52)](https://github.com/user-attachments/assets/600ad519-f8b6-447b-b981-50c078653cd8)
