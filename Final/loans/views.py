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
@login_required
def verify_pan(request):
    context = {}

    if request.method == "POST":
        pan_number = request.POST.get("pan_number")
        full_name = request.POST.get("full_name").strip()  # Strip any leading/trailing spaces
        raw_dob = request.POST.get("dob").strip()  # Strip any leading/trailing spaces

        try:
            dob = f"{raw_dob[4:8]}-{raw_dob[2:4]}-{raw_dob[0:2]}"  # Convert DDMMYYYY to YYYY-MM-DD
        except Exception:
            context['error'] = "Invalid DOB format. Use DDMMYYYY."
            return render(request, 'verify_pan.html', context)

        task_id = str(uuid.uuid4())
        group_id = str(uuid.uuid4())

        headers = {
            "Content-Type": "application/json",
            "account-id": "3fbe2dddab5c/a987487b-fb65-44d3-afdf-f55d4cc92dce",
            "api-key": "8a2b46ba-5f91-4940-b330-3a2b41435081"
        }

        payload = {
            "task_id": task_id,
            "group_id": group_id,
            "data": {
                "id_number": pan_number,
                "full_name": full_name,
                "dob": dob
            }
        }

        try:
            verify_response = requests.post(
                "https://eve.idfy.com/v3/tasks/async/verify_with_source/ind_pan",
                headers=headers, json=payload
            )
            verify_response.raise_for_status()
            response_data = verify_response.json()
            request_id = response_data.get("request_id")

            if not request_id:
                context['error'] = "No request_id returned by IDfy."
                return render(request, 'verify_pan.html', context)

            time.sleep(5)
            status_url = f"https://eve.idfy.com/v3/tasks?request_id={request_id}"
            result_response = requests.get(status_url, headers=headers)
            result_response.raise_for_status()

            # Print the entire result for debugging
            result_list = result_response.json()
            # print("Raw result_list:", json.dumps(result_list, indent=2))  # Debugging the full response

            if result_list and isinstance(result_list, list):
                source_output = result_list[0].get("result", {}).get("source_output", {})
                # print("Source Output:", json.dumps(source_output, indent=2))  # Debugging source output data

                # Check the dob_match and name_match status
                dob_match = source_output.get("dob_match", False)
                name_match = source_output.get("name_match", False)
                
                pan_status = source_output.get("pan_status", "")
                if pan_status == "Existing and Valid. PAN is Operative":
                    profile = UserProfile.objects.get(user=request.user)
                    profile.pan = "Yes"
                    profile.save()
                    request.session["pan_verified"] = True  # For showing animation once
                    return redirect("profile")  # Or your actual profile view name

                else:
                    context["error"] = "PAN is not valid or operative."
                    # context["result"] = json.dumps(result_list, indent=2)
                    return render(request, 'verify_pan.html', context)
               
                if not dob_match:
                    context["error"] = f"Date of birth does not match."
                    # context["result"] = json.dumps(result_list, indent=2)
                    return render(request, 'verify_pan.html', context)

                if not name_match:
                    context["error"] = f"Name does not match."
                    # context["result"] = json.dumps(result_list, indent=2)
                    return render(request, 'verify_pan.html', context)

                # print("Pan Status:", pan_status)  # Check what the pan_status actually is

            else:
                context["error"] = "Unexpected result format."
                # context["result"] = json.dumps(result_list, indent=2)
                return render(request, 'verify_pan.html', context)

        except requests.RequestException as e:
            context['error'] = f"Request failed: {str(e)}"
            return render(request, 'verify_pan.html', context)

    return render(request, "verify_pan.html", context)

def option(request):
    return render(request,"base.html")

@profile_completion_required
def borrower_dashboard(request):
    offers = LoanOffer.objects.all()

    min_amount = request.GET.get('minAmount')
    max_interest = request.GET.get('maxInterest')
    tenor = request.GET.get('tenor')

    try:
        if min_amount:
            min_amount = int(min_amount)
            offers = offers.filter(amount__lte=min_amount)

        if max_interest:
            max_interest = float(max_interest)
            offers = offers.filter(interest_rate__lte=max_interest)

        if tenor:
            tenor_map = {
                "3 months": 3,
                "6 months": 6,
                "1 year": 12,
                "2 years": 24,
            }
            months = tenor_map.get(tenor)
            if months:
                offers = offers.filter(duration_months=months)
    except (ValueError, TypeError):
        messages.error(request, "Invalid filter input.")

    return render(request, 'borrower_dashboard.html', {
        'offers': offers,
        'user': request.user,
    })

@profile_completion_required
def lender_dashboard(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        interest_rate = request.POST.get('interest_rate')
        duration_months = request.POST.get('duration_months')

        if amount and interest_rate and duration_months:
            LoanOffer.objects.create(
                lender=request.user,
                amount=amount,
                interest_rate=interest_rate,
                duration_months=duration_months
            )
        return redirect('lender_dashboard')

    offers = LoanOffer.objects.filter(lender=request.user)
    total_invested_raw = offers.aggregate(Sum('amount'))['amount__sum'] or 0
    average_return = offers.aggregate(Avg('interest_rate'))['interest_rate__avg'] or 0
    active_loans = offers.exclude(borrower__isnull=True).count()
    total_invested = f"{total_invested_raw:,}"

    context = {
        'offers': offers,
        'total_invested': total_invested,
        'average_return': round(average_return, 2),
        'active_loans': active_loans,
    }
    return render(request, 'lender_dashboard.html', context)
