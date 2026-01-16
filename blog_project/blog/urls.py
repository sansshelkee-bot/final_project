# blog/urls.py - FIXED VERSION
from django.urls import path
from . import views

urlpatterns = [
    # Home and basic pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Post URLs
    path('posts/', views.post_list, name='post_list'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_update, name='post_update'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    
    # Filtering URLs
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('search/', views.post_list, name='search'),
    path('categories/', views.all_categories, name='all_categories'),
        path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # Placeholder URLs for missing features
    path('register/', views.home, name='register'),  # Temporary - points to home

    path('profile/', views.home, name='profile'),    # Temporary - points to home

]