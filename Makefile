.PHONY: tests

tests: tests-unit

tests-unit:
	pipenv run python manage.py test djangoapps/

data-pipeline: makemigrations migrate

makemigrations:
	pipenv run python manage.py makemigrations

migrate:
	pipenv run python manage.py migrate

sample-data:
	pipenv run python manage.py loaddata sample-admin.yaml
	pipenv run python manage.py loaddata sample-persons.yaml
	pipenv run python manage.py loaddata sample-course-hp.yaml
	pipenv run python manage.py loaddata sample-course-hpi.yaml

data:
	mkdir -p data

dump-course: data
	pipenv run python manage.py dumpdata lms.Course lms.Section lms.Unit lms.Task lms.Content --format yaml --natural-primary --natural-foreign > data/course.yaml

dump-persons: data
	pipenv run python manage.py dumpdata lms.Person lms.Participant --format yaml --natural-primary --natural-foreign > data/persons.yaml

dump-auth: data
	pipenv run python manage.py dumpdata authtoken lms.UserPerson --format yaml --natural-primary --natural-foreign > data/auth.yaml


dump-all: dump-course dump-persons dump-auth

venv:
	pipenv update --dev

