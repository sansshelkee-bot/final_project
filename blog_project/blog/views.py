# blog/views.py - CLEAN WORKING VERSION
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User  # ADD THIS
from .models import Post, Category
from comments.models import Comment  # Make sure this import works
from .forms import PostForm, CommentForm

def home(request):
    featured_posts = Post.objects.filter(
        status='published', 
        featured=True
    ).order_by('-created_date')[:3]
    
    recent_posts = Post.objects.filter(
        status='published'
    ).order_by('-created_date')[:5]
    categories = Category.objects.all()

    
    context = {
        'featured_posts': featured_posts,
         'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'home.html', context)

def post_list(request):
    posts_list = Post.objects.filter(status='published').order_by('-created_date')
    
    query = request.GET.get('q')
    if query:
        posts_list = posts_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts_list = posts_list.filter(categories=category)
    
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    comments = post.comments.filter(active=True)
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/post_detail.html', context)

def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    messages.success(request, 'Post liked!')
    return redirect('post_detail', slug=post.slug)

# blog/views.py - Update post_create view
@login_required
def post_create(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Ensure publish_date is set if post is published
            if post.status == 'published' and not post.publish_date:
                post.publish_date = timezone.now()
            
            # Save the post (slug will be auto-generated in model's save() method)
            post.save()
            form.save_m2m()  # Save many-to-many data (tags)
            
            messages.success(request, 'Your post has been created successfully!')
            
            # Redirect to the new post
            return redirect('post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'title': 'Create New Post',
    }
    return render(request, 'blog/post_form.html', context)
@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST,request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted!')
        return redirect('post_list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

# SINGLE about() FUNCTION - REMOVE DUPLICATE
def about(request):
    try:
        # Get statistics for the about page
        context = {
            'total_posts': Post.objects.filter(status='published').count(),
            'total_users': User.objects.count(),
            'total_comments': Comment.objects.count() if hasattr(Comment, 'objects') else 0,
            'total_categories': Category.objects.count(),
            'categories': Category.objects.annotate(post_count=Count('post')).order_by('-post_count')[:10],
            'recent_posts': Post.objects.filter(status='published').order_by('-created_date')[:5],
        }
        return render(request, 'blog/about.html', context)
    except Exception as e:
        # Fallback if there are issues
        print(f"About page error: {e}")
        return render(request, 'blog/about.html', {})

# SINGLE contact() FUNCTION - REMOVE DUPLICATE
def contact(request):
    return render(request, 'blog/contact.html')



# blog/views.py - Update contact view
def contact(request):
    """Contact page with debug info"""
    print("=== CONTACT VIEW CALLED ===")
    print(f"Request method: {request.method}")
    print(f"User: {request.user}")
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        print(f"Form data: {name}, {email}, {subject}, {message}")
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    # Add debug context
    context = {
        'debug': True,
        'template_path': 'blog/contact.html',
        'user_authenticated': request.user.is_authenticated,
    }
    
    print(f"Rendering template: blog/contact.html")
    return render(request, 'blog/contact.html', context)


def category_posts(request, slug):
    """Display all posts in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, 
        status='published'
    ).order_by('-publish_date')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_posts.html', context)


# blog/views.py - Add this function
def all_categories(request):
    """Display all categories with post counts"""
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'blog/all_categories.html', context)








# Alternative if Post has ManyToManyField to User for likes
@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.user in post.likes.all():
        # Unlike
        post.likes.remove(request.user)
        messages.info(request, 'Post unliked!')
    else:
        # Like
        post.likes.add(request.user)
        messages.success(request, 'Post liked!')
    
    return redirect('post_detail', slug=post.slug)


from django.shortcuts import render, get_object_or_404
from .models import Category

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.post_set.filter(status='published').order_by('-created_at')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_detail.html', context)