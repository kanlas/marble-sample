from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('ideate/', views.ideate, name='ideate'),
    path('user/<str:username>/update/<int:idea_id>/', views.update_idea, name='update'),
    path('user/<str:username>/delete/<int:idea_id>/', views.delete_idea, name='delete'),
    path('user/<str:username>/remove/<str:follower>/', views.remove_follower, name='remove'),
    path('user/<str:username>/approve/<str:follower>/', views.approve_follower, name='approve'),
    path('user/<str:username>/ideas/', views.manage_ideas, name='ideas'),
    path('user/<str:username>/follows/', views.manage_follows, name='follows'),
    path('user/<str:username>/', views.user, name='user'),
    path('', views.index, name='index'),
]