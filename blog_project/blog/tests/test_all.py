# Navigate to your project
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Category
from django.utils import timezone

class AllTests(TestCase):
    def setUp(self):
        '''Setup test data'''
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='Test content',
            publish_date=timezone.now(),
            status='published'
        )
        self.post.categories.add(self.category)
    
    def test_1_home_page(self):
        '''Test home page loads'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print('✅ Home page works')
    
    def test_2_post_list(self):
        '''Test post list page'''
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        print('✅ Post list page works')
    
    def test_3_post_detail(self):
        '''Test post detail page'''
        response = self.client.get(f'/post/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)
        print('✅ Post detail page works')
    
    def test_4_admin_login(self):
        '''Test admin page loads'''
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirects to login
        print('✅ Admin page redirects to login (good)')
    
    def test_5_basic_math(self):
        '''Sanity check'''
        self.assertEqual(1 + 1, 2)
        print('✅ Basic math works')