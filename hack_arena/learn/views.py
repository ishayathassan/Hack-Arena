from django.shortcuts import render



# Create your views here.

def learn_home(request):
    return render(request, 'learn/learn_home.html')

def python_home(request):
    return render(request, 'learn/learn_python.html')

def cpp_home(request):
    return render(request, 'learn/learn_cpp.html')