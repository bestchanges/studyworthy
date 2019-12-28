init-data:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate
	pipenv run python manage.py loaddata fixtures/test-data.yaml

venv:
	pipenv update --dev
