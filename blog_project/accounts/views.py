from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Sum, Count

# Import your forms and models
from .forms import UserRegistrationForm, UserProfileForm
from .models import Profile

# Import from blog app if needed
try:
    from blog.models import Post
except ImportError:
    # Create a dummy Post model if blog app doesn't exist yet
    class Post:
        objects = None

# Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Registration successful.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Profile View
@login_required
def profile_view(request):
    user = request.user
    
    # Try to get posts if blog app exists
    try:
        from blog.models import Post
        posts = user.blog_posts.all().order_by('-created_at')
        
        # Calculate statistics
        total_views = posts.aggregate(Sum('views'))['views__sum'] or 0
        total_likes = sum(post.likes.count() for post in posts) if hasattr(posts.first(), 'likes') else 0
        published_count = posts.filter(status='published').count()
        draft_count = posts.filter(status='draft').count()
        avg_views = total_views / published_count if published_count > 0 else 0
        
        # Get liked posts if likes field exists
        liked_posts = []
        if hasattr(Post.objects, 'filter'):
            try:
                liked_posts = Post.objects.filter(likes=user)[:5]
            except:
                liked_posts = []
    except:
        # Fallback if blog app doesn't exist
        posts = []
        total_views = 0
        total_likes = 0
        published_count = 0
        draft_count = 0
        avg_views = 0
        liked_posts = []
    
    context = {
        'user': user,
        'posts': posts,
        'total_views': total_views,
        'total_likes': total_likes,
        'published_count': published_count,
        'draft_count': draft_count,
        'avg_views': avg_views,
        'liked_posts': liked_posts,
        'saved_posts': [],
    }
    return render(request, 'accounts/profile.html', context)

# Profile Update View (Class-Based)
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self):
        # Get or create profile for the user
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully!')
        return reverse('profile_view')

# Simple Profile Edit View (Function-Based - Alternative)
@login_required
def profile_edit(request):
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

# Update Profile View (For Form Submission in Profile Page)
@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update profile fields
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        profile.website = request.POST.get('website', profile.website)
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_view')
    
    return redirect('profile_view')

# Update Avatar Only
@login_required
def update_avatar(request):
    if request.method == 'POST' and 'avatar' in request.FILES:
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile picture updated!')
    
    return redirect('profile_view')