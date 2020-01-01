convert-course-to-fixture:
	pipenv run python wlms_import.py courses/hpi/course.yaml  > ../../out/course-fixture.yaml
	cd ../../ && make load-course
