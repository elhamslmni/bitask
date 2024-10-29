from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('posts/', views.all_posts, name='list_posts'),
    path('posts/<int:post_id>/rate/', views.rate_post, name='rate_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.create_post, name='post_create'),
]