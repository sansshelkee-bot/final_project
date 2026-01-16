from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Category
from django.utils import timezone

class UserFlowTestCase(TestCase):
    """Test complete user flows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
    
    def test_complete_post_creation_flow(self):
        """Test complete flow: login -> create post -> view post"""
        # 1. Login
        login_success = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(login_success)
        
        # 2. Access create post page
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Create post
        post_data = {
            'title': 'New Test Post',
            'content': 'This is the content of the new post.',
            'excerpt': 'Brief excerpt',
            'categories': [self.category.id],
            'status': 'published',
        }
        
        response = self.client.post(reverse('create_post'), post_data)
        
        # Should redirect to post detail
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify post was created
        post = Post.objects.get(title='New Test Post')
        self.assertEqual(post.author.username, 'testuser')
        self.assertEqual(post.status, 'published')
        
        # 5. View the created post
        response = self.client.get(
            reverse('post_detail', kwargs={'slug': post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Test Post')
    
    def test_comment_flow(self):
        """Test: view post -> add comment -> see comment"""
        # Create a post
        post = Post.objects.create(
            title='Comment Test Post',
            slug='comment-test-post',
            author=self.user,
            content='Post content',
            publish_date=timezone.now(),
            status='published'
        )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Add comment
        comment_data = {
            'content': 'This is a test comment on the post.',
        }
        
        response = self.client.post(
            reverse('add_comment', kwargs={'post_slug': post.slug}),
            comment_data
        )
        
        # Should redirect back to post
        self.assertEqual(response.status_code, 302)
        
        # Verify comment was added
        response = self.client.get(
            reverse('post_detail', kwargs={'slug': post.slug})
        )
        self.assertContains(response, 'This is a test comment')
    
    def test_search_and_filter_flow(self):
        """Test search and filter functionality"""
        # Create test posts
        for i in range(5):
            Post.objects.create(
                title=f'Test Post {i}',
                slug=f'test-post-{i}',
                author=self.user,
                content=f'Content {i}',
                publish_date=timezone.now(),
                status='published'
            )
        
        # Test search
        response = self.client.get(reverse('post_list'), {'q': 'Test Post 1'})
        self.assertContains(response, 'Test Post 1')
        
        # Test category filter
        post = Post.objects.first()
        post.categories.add(self.category)
        post.save()
        
        response = self.client.get(
            reverse('post_list'),
            {'category': self.category.slug}
        )
        self.assertContains(response, self.category.name)