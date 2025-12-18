"""
Generate and manage document lists with metadata.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    """Document information class."""
    filename: str
    description: str
    category: str = ""
    upload_date: str = ""
    chunks: int = 0
    size_mb: float = 0.0


class DocumentSet:
    """Manages a set of related documents."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.documents: List[Document] = []
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_document(self, filename: str, description: str, category: str = "", 
                    chunks: int = 0, size_mb: float = 0.0) -> None:
        """Add a document to the set."""
        doc = Document(
            filename=filename,
            description=description,
            category=category,
            upload_date=datetime.now().strftime("%Y-%m-%d"),
            chunks=chunks,
            size_mb=size_mb
        )
        self.documents.append(doc)
    
    def print_formatted(self) -> str:
        """Return formatted document list as string."""
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"📚 {self.name}")
        output.append(f"{'='*80}\n")
        
        if self.description:
            output.append(f"{self.description}\n")
        
        for idx, doc in enumerate(self.documents, 1):
            output.append(f"{idx}. {doc.filename}")
            if doc.description:
                output.append(f"   📝 {doc.description}")
            if doc.category:
                output.append(f"   📂 Category: {doc.category}")
            if doc.chunks:
                output.append(f"   🔗 Chunks: {doc.chunks}")
            if doc.size_mb:
                output.append(f"   📦 Size: {doc.size_mb:.2f} MB")
            output.append("")
        
        output.append(f"{'='*80}")
        output.append(f"Total Documents: {len(self.documents)}")
        output.append(f"{'='*80}\n")
        
        return "\n".join(output)
    
    def print_simple(self) -> str:
        """Return simple numbered list."""
        output = []
        output.append(f"\n{self.name}\n")
        for idx, doc in enumerate(self.documents, 1):
            output.append(f"{idx}. {doc.filename} - {doc.description}")
        output.append("")
        return "\n".join(output)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "created_date": self.created_date,
            "documents": [
                {
                    "filename": doc.filename,
                    "description": doc.description,
                    "category": doc.category,
                    "upload_date": doc.upload_date,
                    "chunks": doc.chunks,
                    "size_mb": doc.size_mb
                }
                for doc in self.documents
            ]
        }


# Example: Employee Handbook Set
def create_employee_handbook_set() -> DocumentSet:
    """Create sample Employee Handbook document set."""
    doc_set = DocumentSet(
        name="Employee Handbook Set (Tests policy conflicts)",
        description="Collection of employee policy documents for comprehensive Q&A"
    )
    
    doc_set.add_document(
        filename="employee_handbook_2024.pdf",
        description="General policies and company guidelines",
        category="Core Policies",
        chunks=45,
        size_mb=2.3
    )
    
    doc_set.add_document(
        filename="remote_work_policy_updated.pdf",
        description="Contradicts some handbook rules",
        category="Work Policies",
        chunks=28,
        size_mb=1.1
    )
    
    doc_set.add_document(
        filename="leave_policy_amendment_nov2024.pdf",
        description="Updates original handbook",
        category="Leave & Time Off",
        chunks=35,
        size_mb=1.5
    )
    
    doc_set.add_document(
        filename="expense_reimbursement_guide.pdf",
        description="Specific procedures and guidelines",
        category="Finance Policies",
        chunks=22,
        size_mb=0.8
    )
    
    return doc_set


def create_custom_set(name: str, description: str, documents_list: List[Dict]) -> DocumentSet:
    """Create a custom document set."""
    doc_set = DocumentSet(name=name, description=description)
    
    for doc in documents_list:
        doc_set.add_document(
            filename=doc.get("filename", ""),
            description=doc.get("description", ""),
            category=doc.get("category", ""),
            chunks=doc.get("chunks", 0),
            size_mb=doc.get("size_mb", 0.0)
        )
    
    return doc_set


if __name__ == "__main__":
    # Example usage
    handbook_set = create_employee_handbook_set()
    
    print("\n📋 DETAILED VIEW:")
    print(handbook_set.print_formatted())
    
    print("\n📋 SIMPLE VIEW:")
    print(handbook_set.print_simple())
    
    # Save as JSON
    import json
    with open("document_set.json", "w") as f:
        json.dump(handbook_set.to_dict(), f, indent=2)
    print("✅ Document set saved to document_set.json")
