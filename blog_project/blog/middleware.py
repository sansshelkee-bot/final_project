from django.core.cache import cache
from django.http import HttpResponseForbidden
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rate limit comment submissions
        if request.method == 'POST' and 'comment' in request.path:
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'comment_rate_limit_{ip}'
            
            # Allow 5 comments per minute
            request_count = cache.get(cache_key, 0)
            
            if request_count >= 5:
                return HttpResponseForbidden(
                    "Too many comments. Please wait a minute before posting again."
                )
            
            # Increment count
            cache.set(cache_key, request_count + 1, 60)  # Expire in 60 seconds
        
        response = self.get_response(request)
        return response