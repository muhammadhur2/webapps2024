from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm


from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to WebApp 2024!")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Adjust the redirect to where you want users to go after registering
    else:
        form = CustomUserCreationForm()
    return render(request, 'register/register.html', {'form': form})
