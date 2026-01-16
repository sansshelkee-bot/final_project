from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_register_view_get(self):
        """Test registration page loads"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_view_post(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('register'), data)
        
        # Should redirect to home after registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_view(self):
        """Test user login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_logout_view(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_profile_view_requires_login(self):
        """Test profile requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'testuser')