from django.urls import path
from . import views

urlpatterns = [
    path('', views.practice_home, name='practice_home'),
    path('problem/<int:id>', views.problem_home, name='problem_home'),
    path('submission/<int:id>/', views.submission, name='submission'),
]
