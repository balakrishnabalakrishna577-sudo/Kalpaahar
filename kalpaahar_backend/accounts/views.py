from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to KalpAahar, {user.name or user.email}!')
        return redirect('/')
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = LoginForm(request.POST or None, request=request)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.name or user.email}!')
        next_url = request.GET.get('next', '/')
        return redirect(next_url)
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('/')


def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({'logged_in': True, 'name': request.user.name or request.user.email, 'email': request.user.email})
    return JsonResponse({'logged_in': False})
