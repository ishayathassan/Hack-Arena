from django.urls import path
from . import views

urlpatterns = [
    path('', views.compete_home, name='compete_home'),
    path('<int:id>/login/', views.compete_login, name='compete_login'),
    path('<int:id>/leaderboad/', views.contest_leaderboard, name='contest_leaderboard'),
    path('<int:id>/problemset/', views.contest_problemset, name='contest_problemset'),
    path('<int:id>/submissions/', views.contest_submissions, name='contest_submissions'),
    path('<int:contest_id>/problem/<int:problem_id>', views.contest_problem_home, name='contest_problem'),
    
    
]