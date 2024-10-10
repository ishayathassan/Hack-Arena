from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
import time
import json
import base64
from django.utils import timezone
from .models import Contest, ContestProblem, ContestProblemIO, ContestSubmission, Participant
from .forms import ContestLoginForm
# Create your views here.

def compete_home(request):
    contests = Contest.objects.all()
    for contest in contests:
        # Calculate duration in hours and minutes
        hours = contest.duration // 60
        minutes = contest.duration % 60

        # Format duration
        if hours > 0:
            contest.formatted_duration = f"{hours} hour{'s' if hours > 1 else ''}"
            if minutes > 0:
                contest.formatted_duration += f" {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            contest.formatted_duration = f"{minutes} minute{'s' if minutes > 1 else ''}"
    return render(request, 'compete/compete_home.html', {'contests': contests})

def compete_login(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    contest = get_object_or_404(Contest, id=id)
    form = ContestLoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            password = form.cleaned_data['password']
            
            # Check if the entered password matches the contest password
            if password == contest.password:
                # Check if the user is already a participant
                participant, created = Participant.objects.get_or_create(
                    contest=contest, 
                    user=request.user
                )
                
                # If participant is created, they are new to the contest
                if created:
                    messages.success(request, "Successfully joined the contest!")
                else:
                    messages.info(request, "You are already a participant in this contest.")
                
                # Redirect to contest leaderboard
                return redirect('contest_leaderboard', id=contest.id)
            else:
                messages.error(request, "Incorrect contest password. Please try again.")

    return render(request, 'compete/compete_login.html', {'contest': contest, 'form': form})


def contest_leaderboard(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    contest = get_object_or_404(Contest, id=id)
    
    # Get participants ordered by score (highest first)
    participants = Participant.objects.filter(contest=contest).order_by('-score')
    
    # Update the rank of each participant based on their position in the sorted list
    for index, participant in enumerate(participants):
        # Rank starts from 1, so index + 1
        participant.rank = index + 1
        participant.save()

    return render(request, 'compete/contest_leaderboard.html', {'contest': contest, 'participants': participants})

def contest_problem_home(request, contest_id, problem_id):
    if not request.user.is_authenticated:
        return redirect('login')
    problem = get_object_or_404(ContestProblem, problem_id=problem_id)
    contest = get_object_or_404(Contest, id=contest_id)
    
    if request.method == 'POST':
        user = request.user
        language = request.POST.get('language')
        # Call the dummy judge0 function
        judge0_result = judge0(request, problem)

        submission = ContestSubmission.objects.create(
            user=user,
            problem=problem,
            contest=contest,
            status=judge0_result['status'],
            language=language,
            execution_time=judge0_result['execution_time'],
            memory_used=judge0_result['memory_used'],
            submitted_at=timezone.now()
        )

        if judge0_result['status'] == 'AC':
            participant, created = Participant.objects.get_or_create(contest=contest, user=user)

            # Check which problem was solved and add the points only if the problem is being solved for the first time
            if problem.problem_num == 'A' and not participant.problem_a:
                participant.problem_a = True
                participant.score += problem.point  # Add points for problem A
            elif problem.problem_num == 'B' and not participant.problem_b:
                participant.problem_b = True
                participant.score += problem.point  # Add points for problem B
            elif problem.problem_num == 'C' and not participant.problem_c:
                participant.problem_c = True
                participant.score += problem.point  # Add points for problem C

            # Save the updated participant instance
            participant.save()

        return redirect('contest_leaderboard', id=contest.id)

    return render(request, 'compete/problem_home.html', {'problem': problem, 'contest': contest})



def judge0(request, problem):
    submitted_code = request.POST.get('code')
    language = request.POST.get('language', 'C++')  # Default to C++

    submission_url = "https://judge0-ce.p.rapidapi.com/submissions"
    headers = {
        "X-RapidAPI-Key": "9333c2ddf6msh6e58c0a9dedda56p158529jsna804eb403716",  # Replace with your actual API key
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # Fetch only the first test case for the given problem
    test_case = ContestProblemIO.objects.filter(problem=problem).first()

    if not test_case:
        return {
            "status": "NO_TEST_CASE",
            "execution_time": 0,
            "memory_used": 0
        }

    # Prepare payload for the first test case
    payload = {
        "language_id": 54,  # For example, C++ is 54
        "source_code": submitted_code,
        "stdin": test_case.input_data
    }

    # Step 1: Submit the code for execution
    response = requests.post(submission_url, data=json.dumps(payload), headers=headers)
    submission_data = response.json()
    submission_token = submission_data.get("token")

    # Step 2: Check the result using the token
    result_url = f"https://judge0-ce.p.rapidapi.com/submissions/{submission_token}?base64_encoded=true"
    execution_time = 0
    memory_used = 0
    final_status = "Processing"  # Start with processing status

    retry_count = 0
    max_retries = 10  # Set a limit to retries to avoid infinite loops

    while retry_count < max_retries:
        result_response = requests.get(result_url, headers=headers)
        result_data = result_response.json()

        # Ensure the 'status' key exists in the response
        if 'status' in result_data:
            status = result_data["status"]["description"]
            
            # If the status is still processing, wait and retry
            if status in ["In Queue", "Processing"]:
                time.sleep(1)  # Wait for 1 second before checking again
                retry_count += 1
                continue  # Keep checking the status until it's done

            # Ensure that the time and memory values are not None
            execution_time = max(execution_time, float(result_data.get("time", 0.0)))
            memory_used = max(memory_used, float(result_data.get("memory", 0.0)))
            if status != "Accepted":
                final_status = status
                break

            stdout = base64.b64decode(result_data.get("stdout", "")).decode('utf-8')
            if stdout.strip() != test_case.output_data.strip():
                final_status = "WA"  # Wrong Answer
                break

            if status == "Accepted":
                final_status = "AC"
                break
        else:
            print("Waiting for result...")

        time.sleep(1)
        retry_count += 1

    # If max retries exceeded, return a processing error
    if retry_count == max_retries:
        final_status = "Processing Timeout"

    return {
        "status": final_status,
        "execution_time": execution_time,
        "memory_used": memory_used
    }

def contest_submissions(request, id):
    submissions = ContestSubmission.objects.filter(contest=id, user=request.user)
    contest = Contest.objects.get(id=id)
    return render(request, 'compete/contest_submissions.html',{
        'submissions': submissions,
        'contest': contest
    })


def contest_problemset(request,id):
    contest = Contest.objects.get(id=id)
    problemset = ContestProblem.objects.filter(contest=id)
    return render(request, 'compete/contest_problemset.html', {
        'contest': contest,
        'problemset': problemset
    })