from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, LoanApplication, LoanOffer, LendingMLData, Negotiation
from django.shortcuts import get_object_or_404
from .forms import LendingMLForm, ThresholdForm
from django.db.models import Sum, Avg
from django.contrib import messages
import numpy as np
import uuid
import requests
import joblib
import json
import time
import os
from django.views.decorators.http import require_POST


def check_account_verification(user):
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return False
    
    # First check if all profile fields are filled (like your profile completion check)
    profile_complete = all([
        bool(profile.gender),
        bool(profile.married),
        bool(profile.education),
        bool(profile.self_employed),
        profile.income is not None,
        bool(profile.phone_number),
        bool(profile.name),
        profile.pan == 'Yes',
    ])
    
    # Only check bank verification if profile is complete
    return profile_complete and profile.acc_num == 'Yes'

# Custom decorator for account verification requirement
def account_verified(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not check_account_verification(request.user):
            messages.warning(request, "Please complete your profile AND verify your bank account to access this page.")
            return redirect('verify_bank_account')  # Or your preferred redirect
        return view_func(request, *args, **kwargs)
    return _wrapped_view
# Utility function for profile completion check
def check_profile_completion(user):
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return False

    required_fields_filled = all([
        bool(profile.gender),
        bool(profile.married),
        bool(profile.education),
        bool(profile.self_employed),
        profile.income is not None,
        bool(profile.phone_number),
        bool(profile.name),
        profile.pan == 'Yes',
    ])
    
    return required_fields_filled
# Custom decorator for profile completion requirement
def profile_completion_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not check_profile_completion(request.user):
            messages.warning(request, "Please complete your profile to access this page.")
            return redirect('update_profile')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def index(request):
    return render(request, "index.html")

def signup_view(request):
    if request.user.is_authenticated:
        return render(request, "index.html")
    
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            message = "Email is already taken."
            return render(request, 'signup.html', {'message': message})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, phone_number=phone_number, name=name)
        return redirect('login')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return render(request, "index.html")
    if request.method == 'POST':
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']

        user = None
        if '@' in username_or_email:
            user = authenticate(request, email=username_or_email, password=password)
        else:
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
    return render(request, 'index.html')

@login_required
def update_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.gender = request.POST.get('gender', profile.gender)
        profile.married = request.POST.get('married', profile.married)
        profile.education = request.POST.get('education', profile.education)
        profile.dependents = request.POST.get('dependents') or 0
        profile.self_employed = request.POST.get('self_employed', profile.self_employed)
        profile.income = request.POST.get('income') or 0
        profile.name = request.POST.get('name', profile.name)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        if profile.pan != 'Yes':
            profile.pan = request.POST.get('pan', profile.pan)
            profile.save()
            return redirect('/option')

    return render(request, 'update_profile.html', {'user_profile': profile})

@login_required
def verify_pan(request):

    context = {}
    if request.method == "POST":
        pan_number = request.POST.get("pan_number")
        full_name = request.POST.get("full_name").strip()
        raw_dob = request.POST.get("dob").strip()

        try:
            dob = f"{raw_dob[4:8]}-{raw_dob[2:4]}-{raw_dob[0:2]}"
        except Exception:
            context['error'] = "Invalid DOB format. Use DDMMYYYY."
            return render(request, 'verify_pan.html', context)

        task_id = str(uuid.uuid4())
        group_id = str(uuid.uuid4())

        headers = {
            "Content-Type": "application/json",
            "account-id": "430e2251f643/2501cf12-f407-4cf4-aef4-3e1e0f5e5f4a",
            "api-key": "288dcd91-713f-4bba-b8d0-867fbc5178e9"
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

            result_list = result_response.json()
            if result_list and isinstance(result_list, list):
                source_output = result_list[0].get("result", {}).get("source_output", {})
                pan_status = source_output.get("pan_status", "")
                
                if pan_status == "Existing and Valid. PAN is Operative":
                    profile = UserProfile.objects.get(user=request.user)
                    profile.pan = "Yes"
                    profile.save()
                    request.session["pan_verified"] = True
                    return redirect("/option")
                else:
                    context["error"] = "PAN is not valid or operative."
                    return render(request, 'verify_pan.html', context)

        except requests.RequestException as e:
            context['error'] = f"Request failed: {str(e)}"
            return render(request, 'verify_pan.html', context)

    return render(request, "verify_pan.html", context)

@profile_completion_required
def verify_bank_account(request):
    context = {}
    if request.method == "POST":
        bank_account_no = request.POST.get("account_number").strip()
        bank_ifsc_code = request.POST.get("ifsc_code").strip()

        # Generate unique IDs
        task_id = str(uuid.uuid4())
        group_id = str(uuid.uuid4())

        headers = {
            "Content-Type": "application/json",
            "account-id": "430e2251f643/2501cf12-f407-4cf4-aef4-3e1e0f5e5f4a",
            "api-key": "288dcd91-713f-4bba-b8d0-867fbc5178e9"
        }

        payload = {
            "task_id": task_id,
            "group_id": group_id,
            "data": {
                "bank_account_no": bank_account_no,
                "bank_ifsc_code": bank_ifsc_code
            }
        }

        try:
            # Send verification request
            response = requests.post(
                "https://eve.idfy.com/v3/tasks/async/verify_with_source/validate_bank_account",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            request_id = response_data.get("request_id")

            if not request_id:
                context['error'] = "No request_id returned in response. Cannot proceed."
                return render(request, 'verify_bank.html', context)

            time.sleep(5)  # Wait for processing

            # Check verification status
            status_url = f"https://eve.idfy.com/v3/tasks?request_id={request_id}"
            result_response = requests.get(status_url, headers=headers)
            result_response.raise_for_status()
            result_data = result_response.json()

            if isinstance(result_data, list) and len(result_data) > 0:
                task_result = result_data[0]
                
                if task_result.get("status", "").lower() == "completed":
                    result = task_result.get("result", {})
                    
                    # Get names for comparison
                    bank_name = result.get("name_at_bank", "").strip()
                    try:
                        profile = UserProfile.objects.get(user=request.user)
                        user_name = profile.name.strip() if profile.name else ""
                    except UserProfile.DoesNotExist:
                        user_name = ""

                    # Normalize names for comparison
                    def normalize_name(name):
                        name = name.upper()
                        # Remove extra spaces and special characters
                        name = ' '.join(name.split())
                        name = name.replace(".", "").replace(",", "")
                        return name

                    norm_bank_name = normalize_name(bank_name)
                    norm_user_name = normalize_name(user_name)

                    # Check verification conditions
                    if result.get("account_exists", "").upper() == "YES":
                        if norm_bank_name == norm_user_name:
                            profile.acc_num = "Yes"
                            profile.save()
                            context['success'] = "Bank account verified successfully!"
                            request.session["bank_verified"] = True
                        else:
                            context['error'] = (
                                f"Name mismatch. Bank records show: '{bank_name}' "
                                f"while your profile has: '{user_name}'"
                            )
                    else:
                        context['error'] = "Bank account verification failed. Account not found."
                else:
                    context['error'] = f"Verification failed: {task_result.get('message', 'Unknown error')}"
            else:
                context['error'] = "Unexpected response format from verification service."

        except requests.RequestException as e:
            context['error'] = f"Verification service error: {str(e)}"
        except Exception as e:
            context['error'] = f"An unexpected error occurred: {str(e)}"

    return render(request, 'verify_bank.html', context)

@profile_completion_required
def apply_loan(request):
    if request.method == 'POST':
        amount = request.POST['loan_amount']
        term = request.POST['loan_term']
        score = request.POST['credit_score']
        area = request.POST['property_area']
        LoanApplication.objects.create(
            user=request.user,
            loan_amount=amount,
            loan_term=term,
            credit_score=score,
            property_area=area
        )
        return render(request, 'loan_form.html', {'message': 'Loan application submitted!'})
    return render(request, 'loan_form.html')

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

@account_verified
def borrower_dashboard(request):
    # Check if the user's bank account is verified
    if not request.session.get('bank_verified', False):
        messages.error(request, "Please verify your bank account first.")
        return redirect('verify_bank_account')  # Redirect to the bank verification page

    # Check if threshold is predicted
    if not hasattr(request.user, 'lendingmldata') or not request.user.lendingmldata.model_score:
        messages.error(request, "Please predict your credit threshold first.")
        return redirect('predict_threshold')  # Redirect to the threshold prediction page

    # Filter loan offers
    offers = LoanOffer.objects.exclude(lender=request.user)

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
def negotiation_offer(request):
    if request.method == 'POST':
        negotiation_id = request.POST.get('negotiation_id')
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        
        negotiation = get_object_or_404(
            Negotiation, 
            id=negotiation_id, 
            lender=request.user,
            status='pending'  # Only allow actions on pending negotiations
        )
        
        if action == 'accept':
            negotiation.status = 'accepted'
            # Create loan agreement if accepted
            LoanOffer.objects.create(
                lender=negotiation.lender,
                borrower=negotiation.borrower.username,
                amount=negotiation.proposed_amount,
                interest_rate=negotiation.proposed_interest_rate,
                duration_months=negotiation.proposed_duration_months
            )
            messages.success(request, "Offer accepted successfully!")
        elif action == 'reject':
            negotiation.status = 'rejected'
            messages.success(request, "Offer rejected successfully!")
        elif action == 'counter':
            negotiation.status = 'countered'
            messages.success(request, "Counter offer sent successfully!")
        
        negotiation.lender_note = note
        negotiation.save()
        return redirect('negotiation_offer')

    negotiations = request.user.lender_negotiations.select_related(
        'borrower', 'original_offer'
    )
    
    # Get borrower credit info
    borrower_info = {}
    for negotiation in negotiations:
        borrower = negotiation.borrower
        if borrower.id not in borrower_info:
            try:
                ml_data = LendingMLData.objects.get(user=borrower)
                credit_limit = ml_data.model_score
            except LendingMLData.DoesNotExist:
                credit_limit = 0

            active_loans = LoanOffer.objects.filter(borrower=borrower.username)
            total_loans = sum(loan.amount for loan in active_loans)
            remaining_limit = credit_limit - total_loans

            borrower_info[borrower.id] = {
                'credit_limit': credit_limit,
                'total_loans': total_loans,
                'remaining_limit': remaining_limit
            }

    return render(request, 'negotiation_offer.html', {
        'negotiations': negotiations,
        'borrower_info': borrower_info
    })

@account_verified
def negotiation_offer_made(request):
    negotiations = request.user.borrower_negotiations.select_related(
        'lender', 'original_offer'
    )
    return render(request, 'negotiation_offer_made.html', {
        'negotiations': negotiations
    })

@profile_completion_required
def portfolio(request):
    return render(request, "portfolio.html")

def option(request):
    return render(request, "base.html")

@profile_completion_required
def submit_negotiation(request):
    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        amount = request.POST.get('amount')
        interest = request.POST.get('interest')
        duration = request.POST.get('duration')

        original_offer = get_object_or_404(LoanOffer, id=offer_id)

        Negotiation.objects.create(
            borrower=request.user,
            lender=original_offer.lender,
            original_offer=original_offer,
            proposed_amount=amount,
            proposed_interest_rate=interest,
            proposed_duration_months=duration
        )

        messages.success(request, "Your negotiation has been submitted.")
        return redirect('borrower_dashboard')

from django.shortcuts import render
from .forms import ThresholdForm, PDFUploadForm
from .ocr_module import extract_text_from_pdf, extract_credit_report_fields  # adjust import
import joblib
import os
import numpy as np

scaler = joblib.load("ml_models/threshold_scaler.pkl")
model = joblib.load("ml_models/threshold_model.pkl")
feature_names = joblib.load("ml_models/model_features.pkl")
@account_verified
def predict_threshold(request):
    prediction = None

    if request.method == "POST" and 'pdf_file' in request.FILES:
        pdf_form = PDFUploadForm(request.POST, request.FILES)
        if pdf_form.is_valid():
            pdf_file = request.FILES['pdf_file']
            with open("temp_upload.pdf", "wb+") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Extract text and features
            text = extract_text_from_pdf("temp_upload.pdf")
            ocr_data = extract_credit_report_fields(text)

            # Prepare input vector
            input_vector = [float(ocr_data.get(feature, 0.0)) for feature in feature_names]
            input_scaled = scaler.transform([input_vector])
            threshold = model.predict(input_scaled)[0]
            prediction = round(threshold, 2)

            # Save to LendingMLData
            LendingMLData.objects.update_or_create(
                user=request.user,
                defaults={
                    "encoded_input": dict(zip(feature_names, input_vector)),
                    "model_score": prediction
                }
            )

    else:
        pdf_form = PDFUploadForm()

    return render(request, "predict.html", {
        "pdf_form": pdf_form,
        "prediction": prediction
    })