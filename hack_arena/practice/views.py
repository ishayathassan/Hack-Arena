from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
import requests
import time
import json
import base64
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Problem, UsersSubmission, ProblemIO, UserSolvedProblems


# Create your views here.

def practice_home(request):
    # Fetch all problems initially
    problems = Problem.objects.all()

    # Get the search query from the search bar input
    search_query = request.GET.get('search', '')

    # Get the difficulty filter from the dropdown
    difficulty_filter = request.GET.get('difficulty', '')

    # Filter problems based on the search query (title or tags)
    if search_query:
        problems = problems.filter(
            Q(problem_name__icontains=search_query) |
            Q(tags__tag__icontains=search_query)  # Matching tags based on search query
        )

    # Filter problems based on difficulty if it's selected
    if difficulty_filter:
        problems = problems.filter(difficulty_level=difficulty_filter)

    return render(request, 'practice/practice_home.html', {'problems': problems})

def problem_home(request, id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    problem = get_object_or_404(Problem, pk=id)
    User = get_user_model()  # Fetch the custom User model

    if request.method == 'POST':
        # Call the judge0 function to handle code execution
        result = judge0(request, problem)

        # Handle the result (display message, save submission, etc.)
        status = result.get('status')
        execution_time = result.get('execution_time')
        memory_used = result.get('memory_used')
        
        if status == 'AC':
            # Check if the user has solved the problem before
            has_solved_before = UserSolvedProblems.objects.filter(user=request.user, problem=problem).exists()
            if not has_solved_before:
                # Create a new entry in UserSolvedProblems
                UserSolvedProblems.objects.create(user=request.user, problem=problem)
                

        # Save the submission result to the database
        UsersSubmission.objects.create(
            user=request.user,  # Cast request.user explicitly
            problem=problem,
            submitted_at=timezone.now(),
            status=status,
            execution_time=execution_time,
            memory_used=memory_used,
            language=request.POST.get('language', 'C++')
        )
        return redirect('submission', id=id)
    
    return render(request, 'practice/problem_home.html', {'problem': problem})


def submission(request, id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    # Get the problem instance
    problem = get_object_or_404(Problem, problem_id=id)

    # Fetch all submissions made by the logged-in user for this specific problem
    user_submissions = UsersSubmission.objects.filter(user=request.user, problem=problem)

    return render(request, 'practice/submission.html', {'user_submissions': user_submissions, 'problem': problem})


# def judge0(request, problem):
#     # Return a default result without saving anything
#     return {
#         'status': 'AC',  # Default status
#         'execution_time': 1023,  # Dummy execution time
#         'memory_used': 256  # Dummy memory usage in KB
#     }

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
    test_case = ProblemIO.objects.filter(problem=problem).first()

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

# def judge0(request):
    if request.method == 'POST':
        # Get the submitted code from the POST request
        submitted_code = request.POST.get('code')
        
        submission_url = "https://judge0-ce.p.rapidapi.com/submissions"

        # Your Judge0 API Key (for a public or private instance)
        headers = {
            "X-RapidAPI-Key": "9333c2ddf6msh6e58c0a9dedda56p158529jsna804eb403716",  # Replace with your actual API key
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        # The payload containing the code, language, and optional inputs
        payload = {
            "language_id": 54,  # 54 is the language ID for C++
            "source_code": submitted_code,
            "stdin": "10 9"  # Provide two integers as input
        }
        
        # Step 1: Submit the code for execution
        response = requests.post(submission_url, data=json.dumps(payload), headers=headers)
        submission_data = response.json()

        # Extract the token to check the status and get the result later
        submission_token = submission_data.get("token")
        print("Submission Token:", submission_token)

        # Step 2: Check the result using the token, with base64 encoding enabled
        result_url = f"https://judge0-ce.p.rapidapi.com/submissions/{submission_token}?base64_encoded=true"
        # Polling for the result
        while True:
            result_response = requests.get(result_url, headers=headers)
            
            # Print raw result to see the structure and help with debugging
            result_data = result_response.json()
            print("Raw result data:", result_data)  # Debugging purpose
            
            # Check if 'status' exists in the response
            if 'status' in result_data:
                status = result_data["status"]["description"]
                print("Status:", status)

                # If the status is 'Accepted' or 'Compilation Error', process the output
                if status == "Accepted":
                    # Decode base64-encoded output
                    stdout = result_data.get("stdout")
                    if stdout:
                        decoded_stdout = base64.b64decode(stdout).decode('utf-8')
                        print("Execution Result:\n", decoded_stdout)
                        break
                elif status == "Compilation Error":
                    # Decode base64-encoded compilation error
                    compile_output = result_data.get("compile_output")
                    if compile_output:
                        decoded_compile_output = base64.b64decode(compile_output).decode('utf-8')
                        print("Compilation Error:\n", decoded_compile_output)
                    else:
                        print("No compilation output")
                    break
            else:
                print("Status key not found in response, retrying...")
            
            # Wait for 1 second before checking again
            time.sleep(1)
        
        
        # You can now process the code, run it, or save it
        return HttpResponse(f"Code submitted: {submitted_code}")
