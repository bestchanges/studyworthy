admin-user:
	pipenv run python manage.py createsuperuser --username admin --email egor.fedorov@gmail.com

makemigrations:
	pipenv run python manage.py makemigrations

migrate:
	pipenv run python manage.py migrate

sample-data:
	pipenv run python manage.py loaddata fixtures/sample-persons.yaml fixtures/sample-course.yaml

data-pipeline: makemigrations migrate sample-data

dump-data:
	pipenv run python manage.py dumpdata study.Course study.Learning study.Section study.Unit --format yaml --natural-primary --natural-foreign
	# =============================================================
	pipenv run python manage.py dumpdata study.Person study.Participant --format yaml --natural-primary --natural-foreign

venv:
	pipenv update --dev

