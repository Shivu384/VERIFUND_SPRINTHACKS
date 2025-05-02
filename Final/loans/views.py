from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import LendingMLForm
from django.db.models import Sum, Avg
from django.contrib import messages
import numpy as np
import uuid
import requests
import joblib
import json
import time

def index(request):
    return render(request,"index.html")

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        email = request.POST['email']

        # Check if the email is already taken
        if User.objects.filter(email=email).exists():
            message = "Email is already taken."
            return render(request, 'signup.html', {'message': message})
        
        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)

        UserProfile.objects.create(user=user, phone_number=phone_number,name=name)
        # Optionally, create a UserProfile instance if needed

        return redirect('login')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']

        # Try to find user by email or username
        user = None
        if '@' in username_or_email:  # Assuming it's an email address
            user = authenticate(request, email=username_or_email, password=password)
        else:  # Otherwise, assume it's a username
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            message = 'Invalid login credentials'
            return render(request, 'login.html', {'message': message})

    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return render(request,'base.html')
