from django.test import TestCase
from blog.forms import PostForm, CommentForm
from blog.models import Category, Tag
from django.contrib.auth.models import User

class FormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Tech')
        self.tag = Tag.objects.create(name='Python')
    
    def test_post_form_valid(self):
        """Test PostForm with valid data"""
        form_data = {
            'title': 'Test Post',
            'content': 'This is test content',
            'excerpt': 'Test excerpt',
            'categories': [self.category.id],
            'tags': [self.tag.id],
        }
        
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_post_form_invalid(self):
        """Test PostForm with invalid data"""
        form_data = {
            'title': '',  # Empty title - invalid
            'content': 'Content',
        }
        
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_comment_form_valid(self):
        """Test CommentForm with valid data"""
        form_data = {
            'content': 'This is a test comment.',
        }
        
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_comment_form_invalid(self):
        """Test CommentForm with invalid data"""
        form_data = {
            'content': '',  # Empty content - invalid
        }
        
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)