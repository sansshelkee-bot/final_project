# blog/context_processors.py
from .models import Category

def categories(request):
    return {
        'categories': Category.objects.all()
    }

def trending_posts_processor(request):
    from .models import Post
    trending = Post.objects.filter(
        status='published'
    ).order_by('-views', '-publish_date')[:5]
    return {'trending_posts': trending}