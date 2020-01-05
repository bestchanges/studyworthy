tests-unit:
	pipenv run python manage.py test djangoapps/

makemigrations:
	pipenv run python manage.py makemigrations

migrate:
	pipenv run python manage.py migrate

data-pipeline: makemigrations migrate

sample-data:
	pipenv run python manage.py loaddata sample-admin.yaml
	pipenv run python manage.py loaddata sample-persons.yaml
	pipenv run python manage.py loaddata sample-course-hp.yaml
	pipenv run python manage.py loaddata sample-course-hpi.yaml

data:
	mkdir -p data

dump-course: data
	pipenv run python manage.py dumpdata lms.Course lms.Learning lms.Section lms.Unit --format yaml --natural-primary --natural-foreign > data/course.yaml

dump-persons: data
	pipenv run python manage.py dumpdata lms.Person lms.Participant --format yaml --natural-primary --natural-foreign > data/persons.yaml

dump-auth: data
	pipenv run python manage.py dumpdata authtoken lms.UserPerson --format yaml --natural-primary --natural-foreign > data/auth.yaml


dump-all: dump-course dump-persons dump-auth

venv:
	pipenv update --dev

