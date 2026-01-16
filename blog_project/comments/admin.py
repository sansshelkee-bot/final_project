from django.contrib import admin

# Register your models here.
# comments/admin.py
from django.contrib import admin
from .models import Comment

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content_preview', 'created_date', 'active')
    list_filter = ('active', 'created_date', 'post')
    search_fields = ('author__username', 'post__title', 'content')
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(active=False)
    disapprove_comments.short_description = "Disapprove selected comments"

admin.site.register(Comment, CommentAdmin)