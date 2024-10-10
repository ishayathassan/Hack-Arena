from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('add_problem/', views.add_problem, name='add_problem'),
    path('add_contest/', views.add_contest, name='add_contest'),
]
