from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages 

def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Redirect to home after login
        else:
            # Attempt to auto-create superuser if user doesn't exist
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_superuser(username=username, email="", password=password)
                login(request, user)
                messages.success(request, f"Superuser '{username}' created and logged in.")
                return redirect('home')  # Redirect to home after auto-creation
            else:
                messages.error(request, "Invalid credentials. Try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'login_page.html', {'form': form})

def logout_page(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('accounts:login')
