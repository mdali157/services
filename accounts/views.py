from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
# Create your views here.
from django.contrib.auth.models import  User,auth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

def logout_page(request):
  logout(request)
  return redirect('accounts:login')

  # return HttpResponse('<h1>Hello HttpResponse</h1>')


def login_page(request):
  if request.user.is_authenticated:
    return redirect('home')
  else:
    if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)
      if form.is_valid():
        user = form.get_user()
        login(request, user)
        if 'next' in request.POST:
          return redirect(request.POST.get('next'))
        return redirect('home')
  return render(request, 'login_page.html')
