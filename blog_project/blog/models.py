from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        
        return reverse('category_posts', kwargs={'slug': self.slug})
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='publish_date', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(default=timezone.now)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    
    # Media
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Stats
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(
        User, 
        related_name='post_likes',
        blank=True)
    
    class Meta:
        ordering = ['-publish_date']
        indexes = [
            models.Index(fields=['publish_date', 'status']),
            models.Index(fields=['slug']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if empty
        if not self.slug:
            import uuid  # ⭐⭐ THIS IS THE FIX!
            
            # Create base slug from title
            base_slug = slugify(self.title)
            
            # If title is empty or slugify fails, use 'post'
            if not base_slug:
                base_slug = 'post'
            
            # Add UUID to ensure uniqueness
            unique_id = uuid.uuid4().hex[:8]
            self.slug = f"{base_slug}-{unique_id}"
        
        # Ensure slug is unique for the publish date
        original_slug = self.slug
        counter = 1
        while Post.objects.filter(
            slug=self.slug,
            publish_date__date=self.publish_date.date()
        ).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Auto-generate excerpt if empty
        if not self.excerpt and self.content:
            self.excerpt = self.content[:297] + '...' if len(self.content) > 300 else self.content
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
# Add Like model separately
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'