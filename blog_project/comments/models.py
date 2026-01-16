# comments/models.py
from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    # Use string reference to avoid circular import
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, 
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_date']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"