from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('ai-test/', views.ai_test, name='ai_test'),
    path('profile/', views.profile, name='profile'),
    path('save-gesture/', views.save_gesture_result, name='save_gesture'),
    path('user-stats/', views.get_user_stats, name='user_stats'),  # New endpoint
]