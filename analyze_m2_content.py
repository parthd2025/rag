"""
M2 Document Content Analyzer - Examine what's actually in the M2 document
"""
import sys
import os
sys.path.append('backend')

from backend.ingest import DocumentIngestor
import re

def analyze_m2_document_content():
    """Analyze the actual content of M2 mileage documents"""
    
    print("🔍 === M2 Document Content Analysis ===")
    
    doc_dir = "backend/data/documents"
    m2_files = []
    
    # Find M2 files
    for file in os.listdir(doc_dir):
        if file.endswith(('.pdf', '.docx', '.txt', '.md')):
            if 'M2' in file or 'mileage' in file.lower() or 'Mileage' in file:
                m2_files.append(os.path.join(doc_dir, file))
                print(f"✅ Found M2 document: {file}")
    
    if not m2_files:
        print("❌ No M2 documents found!")
        return
    
    # Analyze each M2 document
    ingestor = DocumentIngestor(chunk_size=2000, chunk_overlap=100)  # Large chunks for analysis
    
    for m2_file in m2_files:
        print(f"\n📄 Analyzing: {os.path.basename(m2_file)}")
        print("="*60)
        
        try:
            # Extract full text
            text = ingestor._extract_text(m2_file)
            
            if not text:
                print("❌ No text extracted!")
                continue
            
            print(f"📊 Document Stats:")
            print(f"   - Total length: {len(text)} characters")
            print(f"   - Word count: {len(text.split())}")
            print(f"   - Lines: {len(text.split('\\n'))}")
            
            # Key term analysis
            key_terms = {
                'M2': text.count('M2') + text.count('m2'),
                'mileage': text.lower().count('mileage'),
                'allowance': text.lower().count('allowance'),
                'benefits': text.lower().count('benefits'),
                'transportation': text.lower().count('transportation'),
                'travel': text.lower().count('travel'),
                'reimbursement': text.lower().count('reimbursement'),
                'policy': text.lower().count('policy'),
                'mindbowser': text.lower().count('mindbowser')
            }
            
            print(f"\n🎯 Key Terms Found:")
            for term, count in key_terms.items():
                if count > 0:
                    print(f"   - '{term}': {count} occurrences")
            
            # Extract context around M2 mentions
            print(f"\n📝 M2 Context Samples:")
            m2_contexts = []
            
            # Find all M2 mentions with context
            for match in re.finditer(r'(?i)m2', text):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                if context not in m2_contexts and len(context) > 50:
                    m2_contexts.append(context)
            
            for i, context in enumerate(m2_contexts[:5]):  # Show first 5 contexts
                print(f"   Context {i+1}: ...{context}...")
            
            # Show document structure
            print(f"\n📋 Document Structure Sample:")
            lines = text.split('\\n')[:20]  # First 20 lines
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   Line {i}: {line.strip()[:80]}...")
            
            # Generate optimized search terms
            print(f"\n🔍 Recommended Search Terms for This Document:")
            
            # Extract unique phrases around M2
            phrases = set()
            for context in m2_contexts[:10]:
                words = context.split()
                for j in range(len(words)):
                    if words[j].lower() == 'm2':
                        # Get 3-word phrases around M2
                        start_idx = max(0, j-2)
                        end_idx = min(len(words), j+3)
                        phrase = ' '.join(words[start_idx:end_idx])
                        if len(phrase) > 5:
                            phrases.add(phrase)
            
            for phrase in list(phrases)[:10]:
                print(f"   - '{phrase}'")
                
        except Exception as e:
            print(f"❌ Error analyzing {m2_file}: {e}")
    
    print(f"\n🎯 === Analysis Complete ===")
    print("💡 Recommendations:")
    print("1. Use the exact terms found in the document for queries")
    print("2. Try phrase-based searches from the context samples")
    print("3. Consider document structure when chunking")
    print("4. Ensure key terms are preserved during chunking")

if __name__ == "__main__":
    analyze_m2_document_content()