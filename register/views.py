from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.shortcuts import render





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


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if 'update_profile' in request.POST and user_form.is_valid():
            user_form.save()
            return redirect('profile')
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important for updating session with new password
            return redirect('profile')
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'register/profile.html', {'user_form': user_form, 'password_form': password_form})