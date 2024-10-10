from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from compete.models import Contest, ContestProblem, ContestProblemIO
from practice.models import Problem, ProblemIO, ProblemTag
from datetime import datetime

# Create your views here.

def admin_home(request):
    return render(request, 'admin_panel/admin_home.html', {})

def add_problem(request):
    if request.method == 'POST':
        # Collect basic problem data from the form
        problem_name = request.POST.get('problem_name')
        problem_description = request.POST.get('problem_description')
        difficulty_level = request.POST.get('difficulty_level')
        input_format = request.POST.get('input_format')
        output_format = request.POST.get('output_format')
        problem_type = request.POST.get('problem_type')
        time_limit = request.POST.get('time_limit')
        memory_limit = request.POST.get('memory_limit')

        try:
            # Create the Problem instance
            problem = Problem.objects.create(
                problem_name=problem_name,
                problem_statement=problem_description,
                input_statement=input_format,
                output_statement=output_format,
                difficulty_level=difficulty_level,
                time_limit=time_limit,
                memory_limit=memory_limit
            )

            # Save tags for the problem
            ProblemTag.objects.create(problem=problem, tag=problem_type)

            # Create test cases (ProblemIO)
            test_cases = []
            for i in range(1, 4):  # Assuming 3 test cases
                test_input = request.POST.get(f'testcase{i}_input')
                test_output = request.POST.get(f'testcase{i}_output')

                if test_input and test_output:
                    test_cases.append(ProblemIO(problem=problem, input_data=test_input, output_data=test_output))

            if test_cases:
                ProblemIO.objects.bulk_create(test_cases)

            messages.success(request, 'Problem added successfully!')
            return redirect('admin_home')  # Redirect to the problem list or any other page after success

        except Exception as e:
            print(f"Unsuccessfully! Error: {str(e)}")
            messages.error(request, f'Error occurred: {str(e)}')
            return redirect('admin_home')  # Reload the form in case of error

    return render(request, 'admin_panel/add_problem.html')


def add_contest(request):
    if request.method == 'POST':
        # Collect contest data from the form
        contest_name = request.POST.get('contest_name')
        contest_description = request.POST.get('contest_description')
        contest_date = request.POST.get('contest_date')
        contest_time = request.POST.get('contest_time')
        contest_password = request.POST.get('contest_password')

        # Combine date and time into a single naive DateTime object
        naive_start_time = datetime.strptime(f"{contest_date} {contest_time}", "%Y-%m-%d %H:%M")
        
        # Make the naive datetime aware
        start_time = timezone.make_aware(naive_start_time)

        try:
            # Create the Contest instance
            contest = Contest.objects.create(
                name=contest_name,
                start_time=start_time,
                duration=60,  # Set a default duration or collect it from the form
                host=request.user.username,  # Assuming the host is the currently logged-in user
                details=contest_description,
                password=contest_password if contest_password else None
            )

            # Handle multiple problems
            for i in range(1, 4):  # Assuming 3 problems as per your form
                problem_label = request.POST.get(f'problem{i}_label')  # This is the problem name
                problem_num = request.POST.get(f'problem{i}_number')  # This is the problem number
                problem_description = request.POST.get(f'problem{i}_description')
                problem_time_limit = request.POST.get(f'problem{i}_time_limit')
                problem_memory_limit = request.POST.get(f'problem{i}_memory_limit')
                problem_input_format = request.POST.get(f'problem{i}_input')
                problem_output_format = request.POST.get(f'problem{i}_output')

                # Debug: Print the problem data
                print(f"Problem {i}:")
                print(f"  Label: {problem_label}")
                print(f"  Number: {problem_num}")
                print(f"  Description: {problem_description}")
                print(f"  Time Limit: {problem_time_limit}")
                print(f"  Memory Limit: {problem_memory_limit}")
                print(f"  Input Format: {problem_input_format}")
                print(f"  Output Format: {problem_output_format}")

                # Create the ContestProblem instance only if required data is present
                if problem_label and problem_num and problem_description and problem_time_limit and problem_memory_limit:
                    contest_problem = ContestProblem.objects.create(
                        contest=contest,
                        problem_name=problem_label,  # Set the problem name from the label
                        problem_num=problem_num,      # Set the problem number
                        problem_statement=problem_description,
                        time_limit=int(problem_time_limit) * 1000,  # Convert minutes to milliseconds
                        memory_limit=int(problem_memory_limit),
                        input_statement=problem_input_format,
                        output_statement=problem_output_format,
                        point=100  # You can adjust this as needed
                    )

                    # Create the test cases for the problem
                    for j in range(1, 4):  # Assuming 3 test cases
                        test_input = request.POST.get(f'problem{i}_testcase{j}_input')
                        test_output = request.POST.get(f'problem{i}_testcase{j}_output')

                        # Debug: Print test case data
                        print(f"  Test Case {j}:")
                        print(f"    Input: {test_input}")
                        print(f"    Output: {test_output}")

                        if test_input and test_output:
                            ContestProblemIO.objects.create(
                                problem=contest_problem,
                                input_data=test_input,
                                output_data=test_output
                            )
                else:
                    print(f"Problem {i} data is incomplete. Skipping this problem.")

            messages.success(request, 'Contest added successfully!')
            return redirect('contest_list')  # Redirect to the contest list or any other page after success

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            messages.error(request, f'Error occurred while adding contest: {str(e)}')
            return redirect('admin_home')  # Reload the form in case of error

    return render(request, 'admin_panel/add_contest.html')