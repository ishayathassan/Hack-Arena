from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('my_home/<str:username>', views.my_home, name='my_home'),
    path('my_home/<str:username>/contests', views.my_contests, name='my_contests'),
    
]
