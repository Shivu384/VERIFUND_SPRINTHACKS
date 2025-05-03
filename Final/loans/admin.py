from django.contrib import admin
from .models import UserProfile,LoanOffer,LoanApplication,LendingMLData,Negotiation
admin.site.register(UserProfile)
admin.site.register(LoanApplication)
admin.site.register(LoanOffer)
admin.site.register(LendingMLData)
admin.site.register(Negotiation)
