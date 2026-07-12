install:
	pip install -r requirements.txt

init-db:
	flask --app run.py init-db

run:
	python run.py

test:
	pytest -q

lint:
	ruff check .
