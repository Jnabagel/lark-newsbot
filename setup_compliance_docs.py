"""Script to set up sample compliance documents in the vector store."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.vector_store import VectorStore
from services.embeddings import EmbeddingService
from ingestion.document_loader import DocumentLoader
from ingestion.chunker import Chunker
from datetime import datetime

def setup_sample_docs():
    """Set up sample compliance documents."""
    print("Setting up ComplianceSME vector store...")
    
    # Initialize components
    vector_store = VectorStore()
    loader = DocumentLoader()
    chunker = Chunker(chunk_size=600, chunk_overlap=50)
    
    # Create sample compliance documents
    sample_docs = [
        {
            "content": """
            Compliance Policy: Data Privacy
            
            All employees must adhere to data privacy regulations including GDPR and local data protection laws.
            Personal data must only be collected with explicit consent and used solely for stated purposes.
            Data retention policies require deletion after 7 years unless legal obligations require longer retention.
            All data breaches must be reported within 72 hours to the compliance officer.
            """,
            "file_name": "data_privacy_policy.txt"
        },
        {
            "content": """
            Compliance Policy: Financial Regulations
            
            All financial transactions must be recorded accurately and in accordance with accounting standards.
            Transactions over $10,000 require additional approval from the finance director.
            Monthly financial reports must be submitted by the 5th of each month.
            External audits will be conducted annually by certified auditors.
            """,
            "file_name": "financial_regulations.txt"
        },
        {
            "content": """
            Compliance Policy: Code of Conduct
            
            Employees must maintain professional conduct at all times.
            Conflicts of interest must be disclosed immediately to management.
            Gifts or favors exceeding $100 value must be reported to HR.
            Violations of the code of conduct may result in disciplinary action up to termination.
            """,
            "file_name": "code_of_conduct.txt"
        },
        {
            "content": """
            Compliance Policy: Information Security
            
            All systems must use strong passwords (minimum 12 characters, mixed case, numbers, symbols).
            Multi-factor authentication is required for all remote access.
            Sensitive data must be encrypted both in transit and at rest.
            Security incidents must be reported to IT security within 1 hour of discovery.
            """,
            "file_name": "information_security.txt"
        },
        {
            "content": """
            Compliance Policy: Anti-Corruption
            
            Bribery and corruption in any form is strictly prohibited.
            Due diligence must be performed on all third-party vendors and partners.
            All payments must be properly documented and approved.
            Training on anti-corruption policies is mandatory for all employees annually.
            """,
            "file_name": "anti_corruption.txt"
        }
    ]
    
    # Chunk documents
    chunked_docs = chunker.chunk_documents(sample_docs)
    
    # Add timestamp to each chunk
    timestamp = datetime.now().isoformat()
    for doc in chunked_docs:
        doc["timestamp"] = timestamp
    
    # Add to vector store
    vector_store.add_documents(chunked_docs)
    
    # Show stats
    stats = vector_store.get_collection_stats()
    print(f"\n✅ Successfully added documents to vector store!")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Document Count: {stats['document_count']}")
    print(f"\nYou can now query ComplianceSME with compliance questions.")

if __name__ == "__main__":
    try:
        setup_sample_docs()
    except Exception as e:
        print(f"❌ Error setting up documents: {e}")
        import traceback
        traceback.print_exc()
