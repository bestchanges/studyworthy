admin-user:
	pipenv run python manage.py createsuperuser --username admin --email egor.fedorov@gmail.com

data-pipeline: makemigrations migrate sample-data

makemigrations:
	pipenv run python manage.py makemigrations

migrate:
	pipenv run python manage.py migrate

tests:
	pipenv run python manage.py test

sample-data:
	pipenv run python manage.py loaddata sample-admin.yaml
	pipenv run python manage.py loaddata sample-persons.yaml
	pipenv run python manage.py loaddata sample-course-hp.yaml
	pipenv run python manage.py loaddata sample-course-hpi.yaml

dump-data-course:
	pipenv run python manage.py dumpdata study.Course study.Learning study.Section study.Unit --format yaml --natural-primary --natural-foreign

dump-data-persons:
	pipenv run python manage.py dumpdata study.Person study.Participant --format yaml --natural-primary --natural-foreign

dump-data-auth:
	pipenv run python manage.py dumpdata authtoken auth.user --format yaml --natural-primary --natural-foreign

venv:
	pipenv update --dev

