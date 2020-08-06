from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views

urlpatterns = [
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/", include("users.urls")),
    path('about/', include('django.contrib.flatpages.urls')),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='terms'),
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
]