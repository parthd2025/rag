import sys
import os
sys.path.append('backend')

from backend.ingest import DocumentIngestor
import PyPDF2

def check_pdf_content():
    print("=== PDF Content Analysis ===\n")
    
    docs_dir = "backend/data/documents"
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(docs_dir, pdf_file)
        print(f"📄 Analyzing: {pdf_file}")
        print(f"   Size: {os.path.getsize(file_path):,} bytes")
        
        try:
            # Read PDF content
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                print(f"   Pages: {total_pages}")
                
                # Get first few pages content
                content_sample = ""
                for i in range(min(3, total_pages)):  # First 3 pages
                    try:
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text()
                        content_sample += page_text + "\n"
                    except Exception as e:
                        print(f"   Error reading page {i+1}: {e}")
                
                # Check for key terms
                content_lower = content_sample.lower()
                has_loan = 'loan' in content_lower
                has_policy = 'policy' in content_lower
                has_mindbowser = 'mindbowser' in content_lower
                has_employee = 'employee' in content_lower
                
                print(f"   Contains 'loan': {has_loan}")
                print(f"   Contains 'policy': {has_policy}")
                print(f"   Contains 'mindbowser': {has_mindbowser}")
                print(f"   Contains 'employee': {has_employee}")
                
                if content_sample:
                    print(f"   First 300 characters:")
                    print(f"   '{content_sample[:300]}...'")
                else:
                    print("   ⚠️ No text extracted")
                    
        except Exception as e:
            print(f"   ❌ Error reading PDF: {e}")
        
        print()

if __name__ == "__main__":
    check_pdf_content()