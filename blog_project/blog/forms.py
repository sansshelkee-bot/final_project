# blog/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re

# Import models
from .models import Post
from comments.models import Comment  # Import from comments app

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters.")
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError("Content must be at least 50 characters.")
        return content

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # Now from comments app
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 2:
            raise ValidationError("Comment must be at least 2 characters.")
        return content# blog/forms.py - SIMPLIFIED VERSION
from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Category, Tag

class PostForm(forms.ModelForm):
    # Custom fields if needed
    new_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Add new tags (comma separated)'
        }),
        help_text='Enter new tags separated by commas'
    )
    
    class Meta:
        model = Post
        # Essential fields only
        fields = ['title', 'content', 'category', 'tags', 'image', 'status']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['status'].required = True
        
        # Make other fields optional
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['image'].required = False
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters.")
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError("Content must be at least 50 characters.")
        return content
    
    def save(self, commit=True):
        # Handle new tags
        instance = super().save(commit=False)
        new_tags = self.cleaned_data.get('new_tags', '')
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many
            
            # Create new tags
            if new_tags:
                for tag_name in new_tags.split(','):
                    tag_name = tag_name.strip()
                    if tag_name:
                        tag, created = Tag.objects.get_or_create(
                            name=tag_name,
                            defaults={'slug': tag_name.lower().replace(' ', '-')}
                        )
                        instance.tags.add(tag)
        
        return instance
    


