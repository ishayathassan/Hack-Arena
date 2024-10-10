from django.db import models
from django.conf import settings

# Create your models here.
class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    duration = models.IntegerField()  # In minutes
    host = models.CharField(max_length=255)
    details = models.TextField()
    password = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    
class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem_id = models.AutoField(primary_key=True)
    problem_name = models.CharField(max_length=255)
    problem_num = models.TextField(default='A')
    problem_statement = models.TextField()
    input_statement = models.TextField()
    output_statement = models.TextField()
    time_limit = models.IntegerField()  # In milliseconds
    memory_limit = models.IntegerField()  # In megabytes
    point = models.IntegerField()

    def __str__(self):
        return self.problem_name


class ContestProblemIO(models.Model):
    problem = models.ForeignKey(ContestProblem, related_name='inputs', on_delete=models.CASCADE)
    input_data = models.TextField()  
    output_data = models.TextField() 
    

    def __str__(self):
        return f"Problem: {self.problem.problem_name} -> Input: {self.input_data} - Output: {self.output_data}"
    

class Participant(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    problem_a = models.BooleanField(default=False)
    problem_b = models.BooleanField(default=False)
    problem_c = models.BooleanField(default=False)
    
    
    class Meta:
        unique_together = ('contest', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.contest.name} - {self.score}"
    
class ContestSubmission(models.Model):
    STATUS_CHOICES = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('TLE', 'Time Limit Exceeded'),
        ('ME', 'Memory Limit Exceeded'),
        ('RE', 'Runtime Error'),
        ('CE', 'Compilation Error'),
    ]
    submission_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey(ContestProblem, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=50)
    execution_time = models.FloatField(null=True, blank=True)  # Changed to FloatField
    memory_used = models.FloatField(null=True, blank=True)  # Changed to FloatField

    def __str__(self):
        return f"{self.user.username} - {self.problem.problem_name} - {self.status}"