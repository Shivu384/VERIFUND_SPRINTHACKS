from django import forms

class LendingMLForm(forms.Form):
    """
    Form for collecting data required by the lending ML model.
    """
    month = forms.ChoiceField(
        choices=[
            ('January', 'January'), ('February', 'February'), ('March', 'March'), 
            ('April', 'April'), ('May', 'May'), ('June', 'June'), 
            ('July', 'July'), ('August', 'August')
        ]
    )
    age = forms.CharField(max_length=5)
    occupation = forms.ChoiceField(
        choices=[
            ('Accountant', 'Accountant'), ('Architect', 'Architect'), ('Developer', 'Developer'),
            ('Doctor', 'Doctor'), ('Engineer', 'Engineer'), ('Entrepreneur', 'Entrepreneur'),
            ('Journalist', 'Journalist'), ('Lawyer', 'Lawyer'), ('Manager', 'Manager'),
            ('Mechanic', 'Mechanic'), ('Media_Manager', 'Media_Manager'), ('Musician', 'Musician'),
            ('Scientist', 'Scientist'), ('Teacher', 'Teacher'), ('Writer', 'Writer')
        ]
    )
    annual_income = forms.CharField(max_length=20, help_text="Enter annual income (e.g. 50000)")
    monthly_inhand_salary = forms.FloatField()
    num_bank_accounts = forms.IntegerField()
    num_credit_card = forms.IntegerField()
    interest_rate = forms.FloatField()
    num_of_loan = forms.IntegerField()
    delay_from_due_date = forms.IntegerField()
    num_of_delayed_payment = forms.IntegerField()
    changed_credit_limit = forms.FloatField()
    num_credit_inquiries = forms.IntegerField()
    credit_mix = forms.ChoiceField(
        choices=[('Bad', 'Bad'), ('Standard', 'Standard'), ('Good', 'Good')]
    )
    outstanding_debt = forms.FloatField()
    credit_utilization_ratio = forms.FloatField()
    credit_history_age = forms.IntegerField()
    payment_of_min_amount = forms.ChoiceField(
        choices=[('Yes', 'Yes'), ('No', 'No'), ('NM', 'NM')]
    )
    total_emi_per_month = forms.FloatField()
    amount_invested_monthly = forms.FloatField()
    payment_behaviour = forms.ChoiceField(
        choices=[
            ('High_spent_Large_value_payments', 'High spent - Large value payments'),
            ('High_spent_Medium_value_payments', 'High spent - Medium value payments'),
            ('High_spent_Small_value_payments', 'High spent - Small value payments'),
            ('Low_spent_Large_value_payments', 'Low spent - Large value payments'),
            ('Low_spent_Medium_value_payments', 'Low spent - Medium value payments'),
            ('Low_spent_Small_value_payments', 'Low spent - Small value payments')
        ]
    )
    monthly_balance = forms.FloatField()
    type_of_loan = forms.ChoiceField(
        choices=[
            ('Auto Loan', 'Auto Loan'),
            ('Credit-Builder Loan', 'Credit-Builder Loan'),
            ('Personal Loan', 'Personal Loan'),
            ('Student Loan', 'Student Loan'),
            ('Mortgage Loan', 'Mortgage Loan'),
            ('Auto Loan, Personal Loan', 'Auto Loan, Personal Loan'),
            ('Auto Loan, Student Loan', 'Auto Loan, Student Loan'),
            ('Unknown', 'Unknown')
        ]
    )

from django import forms

class ThresholdForm(forms.Form):
    Annual_Income = forms.FloatField()
    Monthly_Inhand_Salary = forms.FloatField()
    Num_of_Loan = forms.IntegerField()
    Num_of_Delayed_Payment = forms.IntegerField()
    Changed_Credit_Limit = forms.FloatField()
    Outstanding_Debt = forms.FloatField()
    Amount_invested_monthly = forms.FloatField()
    Monthly_Balance = forms.FloatField()
    Credit_History_Age = forms.IntegerField()

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField()