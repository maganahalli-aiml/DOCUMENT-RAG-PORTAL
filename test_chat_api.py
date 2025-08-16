#!/usr/bin/env python3
"""
Test script to check chat API functionality
"""
import requests
import os
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_chat_index():
    """Test the chat indexing endpoint"""
    print("Testing chat index endpoint...")
    
    # Find a test PDF file
    test_files = list(Path("data").rglob("*.pdf"))
    if not test_files:
        print("No PDF files found in data directory")
        return None
    
    test_file = test_files[0]
    print(f"Using test file: {test_file}")
    
    with open(test_file, 'rb') as f:
        files = {'files': (test_file.name, f, 'application/pdf')}
        data = {
            'session_id': 'test_session_123',
            'use_session_dirs': True,
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'k': 5
        }
        
        try:
            response = requests.post(f"{API_BASE}/chat/index", files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                return response.json().get('session_id')
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception during indexing: {e}")
            return None

def test_chat_query(session_id):
    """Test the chat query endpoint"""
    if not session_id:
        print("No session_id available for testing query")
        return
    
    print(f"\nTesting chat query endpoint with session_id: {session_id}")
    
    data = {
        'question': 'What is this document about?',
        'session_id': session_id,
        'use_session_dirs': True,
        'k': 5
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat/query", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception during query: {e}")

def main():
    print("Starting chat API tests...")
    
    # Test indexing first
    session_id = test_chat_index()
    
    # Then test querying
    test_chat_query(session_id)

if __name__ == "__main__":
    main()
