import os
import sys
from typing import List

import yaml


class Model():
    model = None
    required_fields = ()
    optional_fields = ()

    def __init__(self, **kwargs) -> None:
        self.request_data = dict()
        super().__init__()
        for field in self.required_fields:
            if field not in kwargs:
                raise ValueError(f'Missing required field "{field}". The data was: {kwargs}')

        for field in self.required_fields + self.optional_fields:
            if field in kwargs:
                self.request_data[field] = kwargs[field]

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'REST {self.model}: {self.request_data}'

    def to_django_fixture(self):
        return {
            'model': self.model,
            'fields': self.request_data
        }

    def code(self):
        if 'code' in self.request_data:
            return self.request_data['code']
        raise ValueError('No code')


class Course(Model):
    model = 'study.Course'

    required_fields = (
        'title',
        'code',
    )

    optional_fields = (
        'short_description',
        'long_description',
        'notes',
    )


class Section(Model):
    model = 'study.Section'

    required_fields = (
        'name',
        'code',
        'course',
        'order',
    )

    optional_fields = ()


class Unit(Model):
    model = 'study.Unit'

    required_fields = (
        'name',
        'code',
        'slug',
        'course',
        'order',
        'contents',
    )

    optional_fields = (
        'section',
        'description',
        'notes',
    )


class Content(Model):
    model = 'study.Content'

    required_fields = (
        'type',
        'code',
    )

    optional_fields = (
        'text',
        'url',
        'notes',
    )


# TODO: add Tasks from Unit

class YamlLoader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(YamlLoader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            if filename.endswith('.yaml'):
                return yaml.load(f, YamlLoader)
            else:
                return f.read()

YamlLoader.add_constructor('!include', YamlLoader.include)


def import_course_content(data: dict) -> List[Model]:
    result = []
    course_data = dict(data['course'])
    course = Course(**course_data)
    result.append(course.to_django_fixture())
    section_number = 0
    unit_number_across_course = 0
    for section_node in data['sections']:
        section_number += 1
        section_data = dict(section_node)
        section_data['order'] = section_number
        section_data['course'] = [ course.code() ]
        section_data['code'] = f'{course.code()}-{section_number}'
        section = Section(**section_data)
        result.append(section.to_django_fixture())
        unit_number_across_section = 0
        for unit_node in section_node['units']:
            unit_number_across_course += 1
            unit_number_across_section += 1
            unit_data = dict(unit_node)
            unit_data['course'] = [ course.code() ]
            unit_data['section'] = [ section.code() ]
            unit_data['order'] = unit_number_across_section
            unit_data['code'] = f'{section.code()}-{unit_number_across_section}'
            unit_data['slug'] = f'U{section_number}-{unit_number_across_section}'
            if 'tasks' in unit_data:
                unit_data.pop('tasks')
            contents = []
            for content_node in unit_node['contents']:
                content_data = dict(content_node)
                if 'code' not in content_data:
                    if 'name' in content_data:
                        code = f'{unit_data["code"]}-{content_data["name"]}'
                        content_data.pop('name')
                    else:
                        code = f'{unit_data["code"]}-{len(contents) + 1}'
                    content_data['code'] = code
                content = Content(**content_data)
                contents.append(content)
            result += (content.to_django_fixture() for content in contents)
            unit_data['contents'] = [[content.code()] for content in contents]
            unit = Unit(**unit_data)
            result.append(unit.to_django_fixture())
    return result


def load_yaml(filename):
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=YamlLoader)


def save_yaml(data):
    return yaml.safe_dump(data, allow_unicode=True)


if __name__ == '__main__':
    file = sys.argv[1]
    data = import_course_content(load_yaml(file))
    s = save_yaml(data)
    print(s)
