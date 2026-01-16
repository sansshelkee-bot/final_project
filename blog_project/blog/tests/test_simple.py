# Create simple test file
from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_math(self):
        '''Test that 1+1=2'''
        self.assertEqual(1 + 1, 2)
    
    def test_home_page(self):
        '''Test home page loads'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)