from django.urls import path

from . import views

urlpatterns = [
    path('ideate/', views.ideate, name='ideate'),
    path('user/<str:user>/update/<int:idea_id>/', views.update_idea, name='update'),
    path('user/<str:user>/delete/<int:idea_id>/', views.delete_idea, name='delete'),
    path('user/<str:user>/remove/<str:follower>/', views.remove_follower, name='remove'),
    path('user/<str:user>/approve/<str:follower>/', views.approve_follower, name='approve'),
    path('user/<str:user>/ideas/', views.manage_ideas, name='ideas'),
    path('user/<str:user>/follows/', views.manage_follows, name='follows'),
    path('user/<str:user>/', views.user, name='user'),
    path('', views.index, name='index'),
]