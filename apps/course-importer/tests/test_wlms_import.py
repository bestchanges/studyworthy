import pytest
import yaml

from wlms_import import load_yaml, Course, Section, Unit, import_course_content


@pytest.fixture
def yaml_file():
    yield load_yaml('course.yaml')


def test_parse_course():
    data = {
        'title': 'test course',
        'code': 'test-code',
    }
    course = Course(**data)
    print(course)
    assert course

    expected_data_yaml = """
model: study.Course
fields:
    title: test course
    code: test-code
    """
    expected_data = yaml.load(expected_data_yaml)
    assert course.to_django_fixture() == expected_data


def test_parse_section():
    data = {
        'name': 'test course',
        'order': 1,
        'code': "1-1",
        'course': 11,
    }
    section = Section(**data)
    assert section


def test_parse_unit():
    data = {
        'name': 'test course',
        'order': 1,
        'code': "1-1-1",
        'course': 11,
        'section': 12,
        'content_type': 'text/markdown',
        'content': '# Title of 1 st unit',
    }
    course = Unit(**data)
    assert course


def test_import_yaml(yaml_file):
    objects = import_course_content(yaml_file)
    assert len(objects) == 5
    course = objects[0]
    expected_course = {'fields': {'code': 'hp',
            'long_description': """Hello Python long description\nAnother Lone\n# Hello Python header\n""",
            'notes': 'Content repository: https://github.com/bestchanges/hello_python\n',
            'short_description': 'Study python from scratch',
            'title': 'Hello Python'},
 'model': 'study.Course'}
    assert course.to_django_fixture() == expected_course


