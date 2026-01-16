from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from blog import views
from blog.sitemaps import PostSitemap
from accounts import views as account_views   # ✅ FIX 1


sitemaps = {
    'posts': PostSitemap,
}


# Error handlers
def handler400(request, exception=None):
    return render(request, '400.html', status=400)

def handler403(request, exception=None):
    return render(request, '403.html', status=403)

def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', views.home, name='home'),

    # Blog & Comments
    path('blog/', include('blog.urls')),
    path('comment/', include('comments.urls')),

    # Auth
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout'
    ),
    path(
        'accounts/register/',
        account_views.register,   # ✅ now works
        name='register'
    ),

    path(
        'accounts/password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/password_change.html'
        ),
        name='password_change'
    ),
    path(
        'accounts/password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/password_change_done.html'
        ),
        name='password_change_done'
    ),

    # Sitemap (optional but good)
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),

    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
