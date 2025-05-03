from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    MARRIED_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    EDUCATION_CHOICES = [
        ('High School', 'High School'),
        ('Associate Degree', 'Associate Degree'),
        ('Bachelor\'s Degree', 'Bachelor\'s Degree'),
        ('Master\'s Degree', 'Master\'s Degree'),
        ('Doctorate', 'Doctorate'),
    ]
    
    SELF_EMPLOYED_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , blank=True)
    married = models.CharField(max_length=10, choices=MARRIED_CHOICES , blank=True)
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES , blank=True)
    dependents = models.IntegerField(default=0 , blank=True)
    self_employed = models.CharField(max_length=10, choices=SELF_EMPLOYED_CHOICES , blank=True)
    income = models.IntegerField(default=0,  blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    name=models.CharField(blank=True, max_length=50)
    pan=models.CharField(blank=True,default='No', max_length=10,choices=(('Yes', 'Yes'),('No', 'No')))   
    acc_num=models.CharField(blank=True,default='No', max_length=10,choices=(('Yes', 'Yes'),('No', 'No')))   
    num_ver=models.CharField(blank=True,default='No', max_length=10,choices=(('Yes', 'Yes'),('No', 'No')))   

    def __str__(self):
        return self.user.username

class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_amount = models.IntegerField()
    loan_term = models.IntegerField()
    credit_score = models.IntegerField()
    property_area = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class LoanOffer(models.Model):
    lender = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.PositiveIntegerField()
    borrower = models.CharField(max_length=100, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.lender.username} offers ₹{self.amount} at {self.interest_rate}%"
    
class Negotiation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('countered', 'Counter Offered'),
    ]
    
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrower_negotiations')
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lender_negotiations')
    original_offer = models.ForeignKey(LoanOffer, on_delete=models.CASCADE)
    proposed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    proposed_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    proposed_duration_months = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    lender_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

class LendingMLData(models.Model):
    """
    Model to store machine learning predictions for loan applications.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encoded_input = models.JSONField()  # store inputs used in model prediction
    model_score = models.FloatField()  # model's predicted score or output
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"ML Score for {self.user.username}: {self.model_score}"
