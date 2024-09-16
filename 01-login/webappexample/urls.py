from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path('health/', views.health_check, name='health_check'),

    path('userhome/', views.userhome, name='userhome'),
    path('creategoaltitle/', views.creategoaltitle, name='creategoaltitle'),
    path('save-goal-with-steps/', views.save_goal_with_steps, name='save_goal_with_steps'),
    path('goal-list/', views.goal_list, name='goal_list'),
    path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('update_progress/', views.update_progress, name='update_progress'),
    path('save_manual_goal_with_steps/', views.save_manual_goal_with_steps, name='save_manual_goal_with_steps'),
    path('userprogress/', views.userprogress, name='userprogress'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)