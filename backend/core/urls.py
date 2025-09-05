from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # URLs para Temas
    path('themes/', views.theme_list, name='theme_list'),
    path('themes/<int:theme_id>/', views.theme_detail, name='theme_detail'),
    path('themes/create/', views.theme_create, name='theme_create'),
    path('themes/<int:theme_id>/generate-topics/', views.generate_topics, name='generate_topics'),
    path('themes/<int:theme_id>/generate-post/', views.generate_post_from_topic, name='generate_post_from_topic'),
    
    # URLs para Posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/publish/', views.post_publish, name='post_publish'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/improve/', views.post_improve, name='post_improve'),
    path('posts/<int:post_id>/regenerate-image/', views.regenerate_image_prompt, name='regenerate_image_prompt'),
    
    # Tasks
    path('tasks/<str:task_id>/status/', views.check_task_status, name='check_task_status'),
    path('tasks/status/', views.check_theme_status, name='check_theme_status'),
]
