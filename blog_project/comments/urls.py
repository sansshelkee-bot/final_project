from django.urls import path
from . import views

urlpatterns = [
    path('add/<slug:post_slug>/', views.add_comment, name='add_comment'),
    path('<int:pk>/edit/', views.update_comment, name='edit_comment'),
    path('<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:pk>/like/', views.like_comment, name='like_comment'),
]