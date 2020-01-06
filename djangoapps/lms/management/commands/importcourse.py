from django.core.management.base import BaseCommand, CommandError

from lms.importer import load_yaml, import_course_content
from lms.logic import periodic_task_open_lessons, periodic_task_start_learnings


class Command(BaseCommand):
    help = "Import course from yaml"

    def add_arguments(self, parser):
        parser.add_argument('yaml')

    def handle(self, *args, **options):
        filename = options['yaml']
        self.stdout.write(f'Start import Course from {filename}')
        course_data = load_yaml(filename)
        course = import_course_content(course_data)
        self.stdout.write(f'Imported course: {course}')
        self.stdout.write(f'Number of Units: {course.unit_set.count()}')
        self.stdout.write(self.style.SUCCESS('Done'))
