from django.contrib import admin
from .models import Problem, ProblemIO, ProblemTag, UserSolvedProblems


# Register your models here.
admin.site.register(Problem)
admin.site.register(ProblemIO)
admin.site.register(ProblemTag)
admin.site.register(UserSolvedProblems)