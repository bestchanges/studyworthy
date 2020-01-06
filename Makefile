.PHONY: tests

tests: tests-unit

tests-unit:
	pipenv run python manage.py test djangoapps/

data-pipeline: makemigrations migrate git-add-migrations

git-add-migrations:
	git add djangoapps/*/migrations/*

makemigrations:
	pipenv run python manage.py makemigrations

migrate:
	pipenv run python manage.py migrate

sample-data:
	pipenv run python manage.py loaddata sample-persons.yaml
	pipenv run python manage.py loaddata sample-auth.yaml
	pipenv run python manage.py loaddata sample-courses.yaml
	pipenv run python manage.py loaddata sample-learnings.yaml

data:
	mkdir -p data

clean:
	rm -rf data/*

dump-course: data
	pipenv run python manage.py dumpdata lms.Course lms.Section lms.Unit lms.Task lms.Content --format yaml --natural-primary --natural-foreign > data/sample-courses.yaml

dump-learnings: data
	pipenv run python manage.py dumpdata lms.Learning lms.Lesson lms.RoleStudent lms.RoleTeacher --format yaml --natural-primary --natural-foreign > data/sample-learnings.yaml

dump-persons: data
	pipenv run python manage.py dumpdata lms.Person --format yaml --natural-primary --natural-foreign > data/sample-persons.yaml

dump-auth: data
	pipenv run python manage.py dumpdata authtoken rootapp.SiteUser --format yaml --natural-primary --natural-foreign > data/sample-auth.yaml

dump-all: dump-course dump-learnings dump-persons dump-auth

venv:
	pipenv update --dev

