from django.core.management.base import BaseCommand, CommandError

from study.logic import periodic_task_open_lessons, periodic_task_start_learnings


class Command(BaseCommand):
    help = "Run periodic tasks for StudyWorthy. It's safe to run multiple times"

    def handle(self, *args, **options):
        self.stdout.write(f'Started periodic command')
        learnings = periodic_task_start_learnings()
        self.stdout.write(f'Started Learnings: {len(learnings)}')
        lessons = periodic_task_open_lessons()
        self.stdout.write(f'Opened Lessons: {len(lessons)}')
        self.stdout.write(self.style.SUCCESS('Done'))
