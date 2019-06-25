import unittest
from django.test import Client
from django.test import TestCase

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_courses_response(self):
        response = self.client.get('/courses/')
        self.assertEqual(response.status_code, 200)
    
    def test_course_response(self):
        response = self.client.get('/courses/1/')
        self.assertEqual(response.status_code, 200)

    def test_category_response(self):
        response = self.client.get('/category/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_study_response(self):
        response = self.client.get('/study/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_study_unit_response(self):
        response = self.client.get('/study/1/1')
        self.assertEqual(response.status_code, 200)
    
    def test_user_response(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_study_response(self):
        response = self.client.get('/user/study')
        self.assertEqual(response.status_code, 200)
    
    def test_user_settings_response(self):
        response = self.client.get('/user/settings')
        self.assertEqual(response.status_code, 200)
