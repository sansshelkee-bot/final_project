from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from blog.models import Post

class APITestCase(TestCase):
    """Test API endpoints if you have REST API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.post = Post.objects.create(
            title='API Test Post',
            slug='api-test-post',
            author=self.user,
            content='API test content',
            status='published'
        )
    
    def test_post_list_api(self):
        """Test posts list API endpoint"""
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_detail_api(self):
        """Test post detail API endpoint"""
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_comment_create_api(self):
        """Test comment creation API (requires auth)"""
        # Login first
        self.client.force_authenticate(user=self.user)
        
        comment_data = {
            'content': 'API test comment',
            'post': self.post.id,
        }
        
        response = self.client.post('/api/comments/', comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)