from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from djangoapps.lms.models.lms_models import Course


class TestViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='sample-student',
            email='email@sample-student.zzz',
            password='UserPassword'
        )

    def test_home_authenticated(self):
        client: Client = self.client
        assert client.login(username='sample-student', password='UserPassword')
        response = client.get(reverse('lms_cms:student_kabinet'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lms_cms/student_courses.html")

    def test_home_not_authenticated(self):
        client: Client = self.client
        response = client.get(reverse('lms_cms:student_kabinet'))
        self.assertEqual(response.status_code, 302)

    def test_flow_access(self):
        """
        Flow accesible for:
         * ANY it's participant (Teacher, Student, Admin)
         * super admin
        Flow is not accessible:
         * anonymous user -> shall redirect
         * user has not been assigned to the course - 403
         * user assigned to course but participating in OTHER flow - 403
        """
        client: Client = self.client
        course = Course.objects.create()
        flow = course.create_flow()

        # 1. Anonymous user should redirect to login
        flow_view_url = reverse('lms_cms:flow-view', args=[flow.id])
        expected_params = {
            'next': flow_view_url
        }
        expected_redirect_url = f'{reverse("login")}?{urlencode(expected_params)}'

        response = client.get(flow_view_url)
        self.assertRedirects(response, expected_redirect_url)

        # self.fail("Need more cases")
        # 2. Logged user