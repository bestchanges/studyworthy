import os

import yaml

from lms.models.content import Course, Section, Unit, Content, Task


def import_course_content(data: dict) -> Course:
    course_data = dict(data['course'])
    course, created = Course.objects.update_or_create(course_data, code=course_data['code'])
    section_number = 0
    unit_number_across_course = 0
    for section_node in data['sections']:
        section_number += 1
        section_data = dict(section_node)
        section_data['order'] = section_number
        section_data['course'] = course
        section_data['code'] = f'{course.code}-{section_number}'
        section_data.pop('units')
        section, created = Section.objects.update_or_create(section_data, code=section_data['code'])
        unit_number_across_section = 0
        for unit_node in section_node['units']:
            unit_number_across_course += 1
            unit_number_across_section += 1
            unit_data = dict(unit_node)
            unit_data['course'] = course
            unit_data['section'] = section
            unit_data['order'] = unit_number_across_course
            assert unit_data["slug"], "Slug is required for unit {unit_data}"
            unit_data['code'] = f'{course.code}-{unit_data["slug"]}'
            if 'tasks' in unit_data:
                unit_data.pop('tasks')
            if 'contents' in unit_data:
                unit_data.pop('contents')
            unit, created = Unit.objects.update_or_create(unit_data, code=unit_data['code'])
            contents = []
            for content_node in unit_node['contents']:
                content_data = dict(content_node)
                order = len(contents) + 1
                content_data['order'] = order
                if 'code' not in content_data:
                    if 'name' in content_data:
                        code = f'{unit.code}-{content_data["name"]}'
                        content_data.pop('name')
                    else:
                        code = f'{unit_data["code"]}-C{order}'
                    content_data['code'] = code
                content_data['unit'] = unit
                content, created = Content.objects.update_or_create(content_data, code=content_data['code'])
                contents.append(content)
            if 'tasks' in unit_node:
                tasks = []
                for task_node in unit_node['tasks']:
                    task_data = dict(task_node)
                    order = len(tasks) + 1
                    task_data['order'] = order
                    if 'code' not in task_data:
                        code = f'{unit_data["code"]}-T{order}'
                        task_data['code'] = code
                    task_data['unit'] = unit
                    task, created = Task.objects.update_or_create(task_data, code=task_data['code'])
                    tasks.append(task)
    return course


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


def load_yaml(filename):
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=YamlLoader)
