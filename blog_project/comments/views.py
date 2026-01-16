from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Comment
from blog.models import Post
from .forms import CommentForm

# Add Comment View
@login_required
@require_POST
def add_comment(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug, status='published')
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        
        # Handle reply to parent comment
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                pass
        
        comment.save()
        messages.success(request, 'Comment added successfully!')
    
    return redirect('post_detail', slug=post_slug)

# Update Comment View
@login_required
def update_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'comments/comment_form.html', {'form': form, 'comment': comment})

# Delete Comment View
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.user == comment.author or request.user.is_superuser:
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', slug=post_slug)
    
    messages.error(request, 'You are not authorized to delete this comment.')
    return redirect('post_detail', slug=comment.post.slug)

# Like Comment View
@login_required
@require_POST
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    if request.is_ajax():
        return JsonResponse({
            'likes_count': comment.likes.count(),
            'liked': liked
        })
    
    return redirect('post_detail', slug=comment.post.slug)