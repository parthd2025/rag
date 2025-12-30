#!/usr/bin/env python3
"""
Fix metadata by regenerating it from the backup we found earlier.
"""

import json
from pathlib import Path

# The chunk data we found in the metadata file earlier
chunks_data = [
    "Head  Office:  Sterling  Towers,  Office  No 701 and 702,  S No 32, Wing  B, Pan Card  Club  Road,  Baner,  Pune  - 411045  \nRegd  Office  : A-67, Kailash  Nagar,  Gwalior,  MP, 474010",
    "Phone  : +91-9834164732/33,  Website  : www.mindbowser.com  , Email  : contact@mindbowser.com",
    "Employee Loan Policy",
    "Effective  Date:  June  01, 2024",
    "Policy  Owner:  Human  Resources  Department",
    "Purpose",
    "The purpose of this policy is to provide guidelines and procedures for the provision of loans to employees. This policy aims to support employees in managing unexpected financial needs.",
    "Scope",
    "This policy applies to all full -time and part -time employees of Mindbowser who have completed a minimum of 2 years of continuous service with the company. Temporary, contract, consultants and probationary employees are not eligible for loans.",
    "Definition:",
    "Loan:  A sum  of money  lent to an employee  to be repaid  over  a specified  period.",
    "Eligibility Criteria",
    "To be eligible for a loan employees must meet the following criteria:",
    "● Have completed two years of continuous service with Mindbowser. ● Have no outstanding loans or advances with the company. ● Demonstrate a valid financial need (e.g., medical emergencies, unforeseen personal expenses etc). ● Should not be under PIP in the last six months from the date of loan application. ● Should not be serving notice period.",
    "Application Process:",
    "Request Loan Declaration Form:",
    "● Navigate to the HROne portal. ● Go to the \"Request \" section. ● Select the \"Loan\" option.",
    "Head  Office:  Sterling  Towers,  Office  No 701 and 702,  S No 32, Wing  B, Pan Card  Club  Road,  Baner,  Pune  - 411045  \nRegd  Office  : A-67, Kailash  Nagar,  Gwalior,  MP, 474010",
    "Phone  : +91-9834164732/33,  Website  : www.mindbowser.com  , Email  : contact@mindbowser.com",
    "● Complete all necessary details in the form. ● Ensure accuracy and completeness of the information provided. ● Submit the filled Loan Declaration Form through the HROne portal. ● The application will be forwarded to the respective authority for approval.",
    "● If the loan  is approved:  You will receive  a notification  regarding  the approval.\n● If the loan  is not approved:  You will be notified  of the rejection..",
    "**All conditions will be applicable as mentioned in Declaration form.",
    "Approval Process",
    "● The HR Department will review the application and supporting documents and evaluate the loan application. ● The final approval post consultation with the Project Manager and Management will be given by the HR department.",
    "Loan Amount and Terms",
    "● The maximum loan amount shall not exceed 3 times the employee's monthly gross salary or 3 Lakhs whichever is lower. ● Interest will not be applicable on the loan amount. ● Repayment period cannot exceed 12 months. ● Loan repayment will commence from the next payroll cycle after the loan is disbursed and will be deducted monthly.",
    "Repayment Conditions:",
    "● Employees are required to settle any outstanding loan amounts prior to initiating the resignation or notice period. If the loan remains unpaid, an annual interest rate of 10% will be applied to the outstanding balance. ● If an employee resigns or is terminated, they must repay any outstanding loan amount before their last working day. Until this is done, their full and final settlement and relieving documents will not be processed. ● For any questions regarding this policy, employees should contact the HR Department."
]

# Generate metadata for each chunk
metadata = []
for i, chunk in enumerate(chunks_data):
    metadata.append({
        "source_doc": "Loan Policy",
        "chunk_index": i,
        "chunk_length": len(chunk),
        "page": None,
        "section": chunk.split('\n')[0][:50] if chunk else "",
        "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
        "timestamp": "2025-12-30T11:45:00.000000"
    })

# Save the fixed metadata
fixed_data = {
    "chunks": chunks_data,
    "metadata": metadata
}

metadata_path = Path("data/embeddings/metadata.json")
metadata_path.parent.mkdir(parents=True, exist_ok=True)

with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(fixed_data, f, indent=2, ensure_ascii=False)

print(f"✅ Fixed metadata.json with {len(chunks_data)} chunks")
print(f"📁 Saved to: {metadata_path.absolute()}")