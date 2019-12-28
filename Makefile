init-data:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate
	pipenv run python manage.py loaddata fixtures/test-data.yaml

venv:
	pipenv update --dev

dump-data:
	pipenv run python manage.py dumpdata study.Course study.CourseFlow study.FlowSection study.FlowUnit --format yaml
