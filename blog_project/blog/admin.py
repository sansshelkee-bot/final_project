# blog/admin.py - FIXED VERSION
from django.contrib import admin
from .models import Post, Category, Tag, Like
from django.utils.html import format_html

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_date', 'views', 'get_like_count')
    list_filter = ('status', 'created_date', 'author', 'category')  # CHANGED: 'categories' → 'category'
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image',)  # Make sure this field exists in your model
        }),
        ('Metadata', {
            'fields': ('meta_title', 'meta_description', 'tags', 'category')  # CHANGED: 'categories' → 'category'
        }),
        ('Status & Dates', {
            'fields': ('status', 'featured', 'published_date')
        }),
    )
    
    def view_post(self, obj):
        return format_html('<a href="{}" target="_blank">View</a>', obj.get_absolute_url())
    view_post.short_description = 'View on Site'
    
    def get_like_count(self, obj):
        # Count likes from Like model
        return obj.likes.count()
    get_like_count.short_description = 'Likes'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('user__username', 'post__title')

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Like, LikeAdmin)