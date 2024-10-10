from django.contrib import admin
from .models import Contest, ContestProblem, ContestProblemIO, ContestSubmission, Participant

# Register your models here.
admin.site.register(Contest)
admin.site.register(ContestProblem)
admin.site.register(ContestProblemIO)
admin.site.register(ContestSubmission)
admin.site.register(Participant)