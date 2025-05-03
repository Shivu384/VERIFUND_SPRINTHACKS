from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('update_profile/', views.update_profile, name='update_profile'),
    # path('apply_loan/', views.apply_loan, name='apply_loan'),
    path('verify_pan/', views.verify_pan, name='verify_pan'),
    path('lender_dashboard/', views.lender_dashboard, name='lender_dashboard'),
    path('borrower_dashboard/', views.borrower_dashboard, name='borrower_dashboard'),
    path('option/', views.option, name='option'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('negotiation_offer/', views.negotiation_offer, name='negotiation_offer'),
    path('negotiation_offer_made/', views.negotiation_offer_made, name='negotiation_offer_made'),
    path('submit-negotiation/', views.submit_negotiation, name='submit_negotiation'),
    path('predict_threshold/', views.predict_threshold, name='predict_threshold'),
    path('verify_bank/', views.verify_bank_account, name='verify_bank_account'),
    # path('bank-verification/', views.bank_account_verification, name='bank_account_verification'),
    # path('cybercrime-check/', views.cybercrime_check, name='cybercrime_check'),
]
