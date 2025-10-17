#!/usr/bin/env python
import os
import sys

# Add the project directory to Python path
sys.path.append('.')

try:
    from project.models import get_papers_collection
    print("Testing get_papers_collection function...")
    
    papers = get_papers_collection()
    if papers is None:
        print("ERROR: get_papers_collection returned None")
    else:
        print("SUCCESS: get_papers_collection returned collection object")
        print(f"Collection name: {papers.name}")
        
        # Try to count documents
        try:
            count = papers.count_documents({})
            print(f"SUCCESS: Document count: {count}")
        except Exception as e:
            print(f"ERROR: Error counting documents: {e}")
            
except Exception as e:
    print(f"ERROR: Error importing or calling function: {e}")
    import traceback
    traceback.print_exc()
