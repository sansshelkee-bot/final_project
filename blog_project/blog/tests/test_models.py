from django.test import TestCase
from django.contrib.auth.models import User
from blog.models import Post, Category, Tag
from django.utils import timezone

class ModelTests(TestCase):
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        
        self.tag = Tag.objects.create(
            name='Python',
            slug='python'
        )
    
    def test_post_creation(self):
        """Test creating a post"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='Test content',
            excerpt='Test excerpt',
            publish_date=timezone.now(),
            status='published'
        )
        
        post.categories.add(self.category)
        post.tags.add(self.tag)
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author.username, 'testuser')
        self.assertEqual(post.status, 'published')
        self.assertEqual(post.categories.count(), 1)
        self.assertEqual(post.tags.count(), 1)
    
    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Technology')
    
    def test_tag_str(self):
        """Test tag string representation"""
        self.assertEqual(str(self.tag), 'Python')
    
    def test_post_str(self):
        """Test post string representation"""
        post = Post.objects.create(
            title='Sample Post',
            slug='sample-post',
            author=self.user,
            content='Content'
        )
        self.assertEqual(str(post), 'Sample Post')