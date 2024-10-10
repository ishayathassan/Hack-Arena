from django.db import models
from django.conf import settings
from home.models import User

# Create your models here.
class Problem(models.Model):
    problem_id = models.AutoField(primary_key=True)
    problem_name = models.CharField(max_length=255)
    problem_statement = models.TextField()
    input_statement = models.TextField()
    output_statement = models.TextField()
    difficulty_level = models.CharField(max_length=50, default='Easy')
    time_limit = models.IntegerField()  # In milliseconds
    memory_limit = models.IntegerField()  # In megabytes
    is_practice = models.BooleanField(default=True)

    def __str__(self):
        return self.problem_name


class ProblemIO(models.Model):
    problem = models.ForeignKey(Problem, related_name='inputs', on_delete=models.CASCADE)
    input_data = models.TextField()  # Store input as a text field
    output_data = models.TextField()  # Store expected output as a text field
    

    def __str__(self):
        return f"Problem: {self.problem.problem_name} -> Input: {self.input_data} - Output: {self.output_data}"
    

class ProblemTag(models.Model):
    problem = models.ForeignKey(Problem, related_name='tags', on_delete=models.CASCADE)
    tag = models.TextField()
    

    def __str__(self):
        return f"Problem: {self.problem.problem_name} -> Tag: {self.tag}"

class UsersSubmission(models.Model):
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
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=50)
    execution_time = models.IntegerField(null=True, blank=True)  # In milliseconds
    memory_used = models.IntegerField(null=True, blank=True)  # In megabytes

    def __str__(self):
        return f"{self.user.username} - {self.problem.problem_name} - {self.status}"


class UserSolvedProblems(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.problem.problem_name}"
    
    