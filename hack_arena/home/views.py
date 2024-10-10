from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, CustomLoginForm
from practice.models import UserSolvedProblems, UsersSubmission
from compete.models import Contest
# Create your views here.

def home(request):
    return render(request, 'home/home.html', {})

def my_home(request,username):
    if not request.user.is_authenticated:
        return redirect('login')
    solved_count = UserSolvedProblems.objects.filter(user__username=username).count()
    attempts = UsersSubmission.objects.filter(user__username=username).count()
    contest_count = Contest.objects.filter(participant__user=request.user).count()
    submissions = UsersSubmission.objects.filter(user__username=username)
    return render(request, 'home/my_home.html', 
                  {'solved_count': solved_count, 
                   'attempts': attempts, 
                   'submissions': submissions,
                   'contest_count': contest_count})
    
    
def my_contests(request, username):
    if not request.user.is_authenticated:
        return redirect('login')
    solved_count = UserSolvedProblems.objects.filter(user__username=username).count()
    attempts = UsersSubmission.objects.filter(user__username=username).count()
    # Fetch contests that the user has participated in
    contests = Contest.objects.filter(participant__user=request.user)
    contest_count = Contest.objects.filter(participant__user=request.user).count()
    

    # Pass the contests to the template
    return render(request, 'home/my_contests.html', {'contests': contests,
                                                     'contest_count': contest_count,
                                                     'solved_count': solved_count,
                                                     'attempts': attempts})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}! You have successfully logged in.')
                return redirect('home')  # Redirect to home or any other page
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = CustomLoginForm()

    return render(request, 'home/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            login(request, user)
            return redirect('home')  # Redirect to home page or any other page
    else:
        form = SignUpForm()
    
    return render(request, 'home/signup.html', {'form': form})