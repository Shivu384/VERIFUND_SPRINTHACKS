import fitz
import re
import pytesseract
from pdf2image import convert_from_path # type: ignore

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF: use text layer if available, otherwise OCR."""
    doc = fitz.open(pdf_path)
    all_text = ""

    for page in doc:
        text = page.get_text()
        if text.strip():
            all_text += text
        else:
            # OCR fallback
            images = convert_from_path(pdf_path, first_page=page.number + 1, last_page=page.number + 1)
            ocr_text = pytesseract.image_to_string(images[0])
            all_text += ocr_text
    return all_text

def extract_credit_report_fields(ocr_text):
    """Parse extracted text and return structured financial data."""
    data = {}

    # Annual Income
    annual_income_match = re.search(r'2021\s*\$([\d,\.]+)', ocr_text)
    data['Annual_Income'] = float(annual_income_match.group(1).replace(',', '')) if annual_income_match else 0.0

    # Monthly Inhand Salary
    hourly_match = re.search(r'Employee Rate of Pay:\s*\$([\d\.]+)', ocr_text)
    hours_match = re.search(r'Avg\.Hrs\.Worked/Pay Period:\s*(\d+)', ocr_text)
    pay_cycle_match = re.search(r'Pay Cycle:\s*(\w+)', ocr_text)
    if hourly_match and hours_match:
        hourly_rate = float(hourly_match.group(1))
        hours = float(hours_match.group(1))
        pay_cycle = pay_cycle_match.group(1).lower() if pay_cycle_match else 'biweekly'
        multiplier = 2 if pay_cycle == 'biweekly' else 4
        data['Monthly_Inhand_Salary'] = hourly_rate * hours * multiplier
    else:
        data['Monthly_Inhand_Salary'] = 0.0

    # Number of Loans
    accounts = re.findall(r'(Installments|Revolving|Other)\s*\$[\d,\.]+', ocr_text)
    data['Num_of_Loan'] = len(accounts)

    # Number of Delayed Payments
    d30 = int(re.search(r'30 Day Delinquencies:\s*(\d+)', ocr_text).group(1)) if re.search(r'30 Day Delinquencies:\s*(\d+)', ocr_text) else 0
    d60 = int(re.search(r'60 Day Delinquencies:\s*(\d+)', ocr_text).group(1)) if re.search(r'60 Day Delinquencies:\s*(\d+)', ocr_text) else 0
    d90 = int(re.search(r'90 Day Delinquencies:\s*(\d+)', ocr_text).group(1)) if re.search(r'90 Day Delinquencies:\s*(\d+)', ocr_text) else 0
    data['Num_of_Delayed_Payment'] = d30 + d60 + d90

    # Changed Credit Limit
    limits = re.findall(r'Credit Limit:\s*\$([\d,\.]+)', ocr_text)
    data['Changed_Credit_Limit'] = sum(float(lim.replace(',', '')) for lim in limits) if limits else 0.0

    # Outstanding Debt
    balances = re.findall(r'Balance:\s*\$([\d,\.]+)', ocr_text)
    data['Outstanding_Debt'] = sum(float(bal.replace(',', '')) for bal in balances) if balances else 0.0

    # Placeholder values
    data['Amount_invested_monthly'] = 0.0
    data['Monthly_Balance'] = 0.0

    # Credit History Age
    history_match = re.search(r'Length of Credit History:\s*(\d+)\s*years\s*and\s*(\d+)\s*months', ocr_text)
    if history_match:
        years = int(history_match.group(1))
        months = int(history_match.group(2))
        data['Credit_History_Age'] = years * 12 + months
    else:
        data['Credit_History_Age'] = 0

    return data