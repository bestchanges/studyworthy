import os

from django.test import TestCase

from lms.importer import load_yaml, import_course_content
from lms.models.content import Course, Section, Unit, Content, Task


class TestImporter(TestCase):
    BASE_DIR = os.path.dirname(__file__)
    YAML_FILE = os.path.join(BASE_DIR, 'course.yaml')

    def test_load_yaml(self):
        course_data = load_yaml(self.YAML_FILE)
        assert course_data
        assert 'course' in course_data

    def test_new_course(self):
        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(Section.objects.count(), 0)
        self.assertEqual(Unit.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)

        course_data = load_yaml(self.YAML_FILE)
        course = import_course_content(course_data)

        self.assertTrue(course)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Section.objects.count(), 2)
        self.assertEqual(Unit.objects.count(), 3)
        self.assertEqual(Content.objects.count(), 4)
        self.assertEqual(Task.objects.count(), 3)

    # TODO:
    # test_update_existing_course
    # test_update_existing_course_keep_unchanged data
    # test_update_existing_course_delete staled data
    # test_check_for_unique_identifiers_for_objects_in_the_file
