from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand
from djmoney.money import Money

from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Product
from djangoapps.lms.models import Participant, Unit, CourseLesson
from djangoapps.lms_cms.logic.users import create_lms_user
from djangoapps.lms_cms.models import CmsCourse, CmsLesson
from studyworthy import settings

ADMIN_EMAIL = 'admin@studyworty.xyz'
ADMIN_PASSWORD = 'admin'

class Command(BaseCommand):
    help = "Create sample data to fill site with."

    def handle(self, *args, **options):
        call_command('init')
        if not User.objects.filter(username=ADMIN_EMAIL).exists():
            create_lms_user(
                email=ADMIN_EMAIL,
                roles=[Participant.ROLE_TEACHER, Participant.ROLE_ADMIN],
                password=ADMIN_PASSWORD,
            )
            assert User.objects.filter(username=ADMIN_EMAIL).exists()

        # Lesson 1-3
        lesson_promise, _ = CmsLesson.objects.get_or_create(title='Promise')
        lesson_sale, _ = CmsLesson.objects.get_or_create(title='Sale')
        lesson_intro, _ = CmsLesson.objects.get_or_create(title='Introduction')
        lesson_explain, _ = CmsLesson.objects.get_or_create(title='Explaination')
        lesson_extra, _ = CmsLesson.objects.get_or_create(title='Extra')
        lesson_bonus1, _ = CmsLesson.objects.get_or_create(title='Bonus 1')
        lesson_bonus2, _ = CmsLesson.objects.get_or_create(title='Bonus 2')

        # Free Course with 2 lessons in 1 unit
        course_1, _ = CmsCourse.objects.get_or_create(title='Free course')
        unit_1, _ = Unit.objects.get_or_create(course=course_1, name='Interest')
        CourseLesson.objects.get_or_create(unit=unit_1, course=course_1, lesson=lesson_promise)
        CourseLesson.objects.get_or_create(unit=unit_1, course=course_1, lesson=lesson_sale)

        # Payed Course with 3 lessons in 2 units
        course_2, _ = CmsCourse.objects.get_or_create(title='Main course')
        unit_1, _ = Unit.objects.get_or_create(course=course_2, name='Basics')
        CourseLesson.objects.get_or_create(unit=unit_1, course=course_2, lesson=lesson_intro)
        CourseLesson.objects.get_or_create(unit=unit_1, course=course_2, lesson=lesson_explain)
        unit_2, _ = Unit.objects.get_or_create(course=course_2, name='Extra')
        CourseLesson.objects.get_or_create(unit=unit_2, course=course_2, lesson=lesson_extra)

        # Bonus Course with 2 lessons and no units
        course_3, _ = CmsCourse.objects.get_or_create(title='Bonus course')
        CourseLesson.objects.get_or_create(course=course_3, lesson=lesson_bonus1)
        CourseLesson.objects.get_or_create(course=course_3, lesson=lesson_bonus2)

        # Now let's create 2 products Free and Payed
        product_free, _ = CourseProduct.objects.get_or_create(
            name='Free course', state=Product.State.ACTIVE,
            course=course_1,
            price = Money(0, settings.DEFAULT_CURRENCY),
        )

        product_paid, _ = CourseProduct.objects.get_or_create(
            name='Full Course and Bonus',
            state=Product.State.ACTIVE,
            course=course_2,
            price=Money(1.03, settings.DEFAULT_CURRENCY),
        )

        site: Site = Site.objects.get_current()
        site.name =  'IT-Cat'
        site.domain = 'localhost:8000'
        site.save()

        # create_home_page()
        self.stdout.write("Sample data created")
        self.stdout.write(f"Admin user creds: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")