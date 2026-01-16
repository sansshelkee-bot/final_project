# tests/performance/test_performance.py
from django.test import TestCase
from blog.models import Post, Category
from django.contrib.auth.models import User
import time

class PerformanceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            password='testpass123'
        )
        
        # Create test data
        self.category = Category.objects.create(name='Performance')
        
        # Create 100 posts for testing
        for i in range(100):
            Post.objects.create(
                title=f'Performance Post {i}',
                slug=f'performance-post-{i}',
                author=self.user,
                content='x' * 1000,  # 1000 character content
                status='published'
            )
    
    def test_post_list_performance(self):
        """Test post list page performance"""
        start_time = time.time()
        
        # Simulate multiple requests
        for _ in range(10):
            response = self.client.get('/posts/')
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\nPost list performance test:")
        print(f"10 requests completed in {execution_time:.2f} seconds")
        print(f"Average: {execution_time/10:.2f} seconds per request")
        
        # Assert performance threshold (adjust as needed)
        self.assertLess(execution_time, 5.0)  # Should complete in under 5 seconds
    
    def test_database_query_optimization(self):
        """Test that views use efficient queries"""
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        # Access post list
        self.client.get('/posts/')
        
        query_count = len(connection.queries)
        print(f"\nDatabase queries for post list: {query_count}")
        
        # Should use reasonable number of queries
        self.assertLess(query_count, 15)