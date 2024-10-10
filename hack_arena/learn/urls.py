from django.urls import path
from . import views

urlpatterns = [
    path('', views.learn_home, name='learn_home'),
    path('python/', views.python_home, name='python_home'),
    path('cpp/', views.cpp_home, name='cpp_home'),
]