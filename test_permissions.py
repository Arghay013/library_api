#!/usr/bin/env python
"""
Script to test role-based permissions in the Library API
Run: python test_permissions.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# Test credentials
LIBRARIAN_CREDS = {
    "username": "librarian_user",
    "password": "LibrarianPass123!"
}

MEMBER_CREDS = {
    "username": "member_user",
    "password": "MemberPass123!"
}

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_test(text):
    """Print test description"""
    print(f"{Colors.BOLD}{text}{Colors.RESET}")


def get_token(credentials):
    """Get JWT token for a user"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/jwt/create/",
            json=credentials
        )
        if response.status_code == 200:
            return response.json()['access']
        else:
            print_error(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error getting token: {str(e)}")
        return None


def make_request(method, endpoint, token=None, data=None):
    """Make HTTP request to API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, json=data, headers=headers)
        elif method == 'PATCH':
            headers['Content-Type'] = 'application/json'
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return None
        
        return response
    except Exception as e:
        print_error(f"Request error: {str(e)}")
        return None


def test_book_permissions():
    """Test book endpoint permissions"""
    print_header("TESTING BOOK ENDPOINTS")
    
    # Get tokens
    librarian_token = get_token(LIBRARIAN_CREDS)
    member_token = get_token(MEMBER_CREDS)
    
    if not librarian_token or not member_token:
        print_error("Failed to get tokens")
        return
    
    # Test data
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "123-456-789",
        "is_available": True
    }
    
    # Test 1: List books (public, no auth needed)
    print_test("Test 1: GET /api/books/ (No authentication)")
    response = make_request('GET', '/books/')
    if response and response.status_code == 200:
        print_success(f"Books listed successfully (status: {response.status_code})")
    else:
        print_error(f"Failed to list books (status: {response.status_code if response else 'N/A'})")
    
    # Test 2: Create book as librarian (should succeed)
    print_test("Test 2: POST /api/books/ as Librarian (should succeed)")
    response = make_request('POST', '/books/', librarian_token, book_data)
    if response and response.status_code == 201:
        print_success(f"Book created successfully (status: 201)")
        book_id = response.json().get('id')
    else:
        print_error(f"Failed to create book (status: {response.status_code if response else 'N/A'})")
        book_id = None
    
    # Test 3: Create book as member (should fail)
    print_test("Test 3: POST /api/books/ as Member (should fail with 403)")
    response = make_request('POST', '/books/', member_token, book_data)
    if response and response.status_code == 403:
        print_success(f"Permission denied as expected (status: 403)")
    else:
        print_error(f"Expected 403, got {response.status_code if response else 'N/A'}")
    
    # Test 4: Create book without auth (should fail)
    print_test("Test 4: POST /api/books/ without authentication (should fail with 401)")
    response = make_request('POST', '/books/', None, book_data)
    if response and response.status_code == 401:
        print_success(f"Unauthorized as expected (status: 401)")
    else:
        print_error(f"Expected 401, got {response.status_code if response else 'N/A'}")
    
    if book_id:
        # Test 5: Update book as librarian (should succeed)
        print_test("Test 5: PATCH /api/books/{id}/ as Librarian (should succeed)")
        update_data = {"title": "Updated Test Book"}
        response = make_request('PATCH', f'/books/{book_id}/', librarian_token, update_data)
        if response and response.status_code == 200:
            print_success(f"Book updated successfully (status: 200)")
        else:
            print_error(f"Failed to update book (status: {response.status_code if response else 'N/A'})")
        
        # Test 6: Update book as member (should fail)
        print_test("Test 6: PATCH /api/books/{id}/ as Member (should fail with 403)")
        response = make_request('PATCH', f'/books/{book_id}/', member_token, update_data)
        if response and response.status_code == 403:
            print_success(f"Permission denied as expected (status: 403)")
        else:
            print_error(f"Expected 403, got {response.status_code if response else 'N/A'}")
        
        # Test 7: Delete book as librarian (should succeed)
        print_test("Test 7: DELETE /api/books/{id}/ as Librarian (should succeed)")
        response = make_request('DELETE', f'/books/{book_id}/', librarian_token)
        if response and response.status_code == 204:
            print_success(f"Book deleted successfully (status: 204)")
        else:
            print_error(f"Failed to delete book (status: {response.status_code if response else 'N/A'})")


def test_borrow_permissions():
    """Test borrow/return endpoint permissions"""
    print_header("TESTING BORROW/RETURN ENDPOINTS")
    
    # Get tokens
    librarian_token = get_token(LIBRARIAN_CREDS)
    member_token = get_token(MEMBER_CREDS)
    
    if not librarian_token or not member_token:
        print_error("Failed to get tokens")
        return
    
    # First, create a book as librarian
    book_data = {
        "title": "Borrowable Book",
        "author": "Test Author",
        "isbn": "999-888-777",
        "is_available": True
    }
    
    response = make_request('POST', '/books/', librarian_token, book_data)
    if response and response.status_code == 201:
        book_id = response.json().get('id')
    else:
        print_error("Failed to create test book for borrowing")
        return
    
    # Test 1: Borrow as member (should succeed)
    print_test("Test 1: POST /api/borrow/ as Member (should succeed)")
    borrow_data = {
        "book": book_id,
        "member": 1
    }
    response = make_request('POST', '/borrow/', member_token, borrow_data)
    if response and response.status_code == 200:
        print_success(f"Book borrowed successfully (status: 200)")
    else:
        print_error(f"Failed to borrow book (status: {response.status_code if response else 'N/A'})")
    
    # Test 2: Borrow without auth (should fail)
    print_test("Test 2: POST /api/borrow/ without authentication (should fail with 401)")
    response = make_request('POST', '/borrow/', None, borrow_data)
    if response and response.status_code == 401:
        print_success(f"Unauthorized as expected (status: 401)")
    else:
        print_error(f"Expected 401, got {response.status_code if response else 'N/A'}")
    
    # Test 3: Return as member (should succeed)
    print_test("Test 3: POST /api/return/ as Member (should succeed)")
    return_data = {
        "book": book_id,
        "member": 1
    }
    response = make_request('POST', '/return/', member_token, return_data)
    if response and response.status_code == 200:
        print_success(f"Book returned successfully (status: 200)")
    else:
        print_error(f"Failed to return book (status: {response.status_code if response else 'N/A'})")


def test_authentication_flow():
    """Test authentication flow"""
    print_header("TESTING AUTHENTICATION FLOW")
    
    # Test 1: Register/Login as librarian
    print_test("Test 1: Login as Librarian")
    response = requests.post(
        f"{BASE_URL}/auth/jwt/create/",
        json=LIBRARIAN_CREDS
    )
    if response.status_code == 200:
        token = response.json().get('access')
        print_success(f"Login successful, token acquired (status: 200)")
        
        # Test 2: Verify token
        print_test("Test 2: Verify Token")
        verify_response = requests.post(
            f"{BASE_URL}/auth/jwt/verify/",
            json={"token": token}
        )
        if verify_response.status_code == 200:
            print_success(f"Token verified successfully (status: 200)")
        else:
            print_error(f"Failed to verify token (status: {verify_response.status_code})")
    else:
        print_error(f"Login failed (status: {response.status_code})")
    
    # Test 3: Login as member
    print_test("Test 3: Login as Member")
    response = requests.post(
        f"{BASE_URL}/auth/jwt/create/",
        json=MEMBER_CREDS
    )
    if response.status_code == 200:
        print_success(f"Login successful (status: 200)")
    else:
        print_error(f"Login failed (status: {response.status_code})")


def main():
    """Run all permission tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("LIBRARY API - ROLE-BASED PERMISSIONS TEST SUITE")
    print(f"{'='*60}{Colors.RESET}")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run test suites
        test_authentication_flow()
        test_book_permissions()
        test_borrow_permissions()
        
        # Summary
        print_header("TEST SUITE COMPLETED")
        print_success("All tests completed. Review results above.")
        
    except KeyboardInterrupt:
        print("\n" + Colors.YELLOW + "Tests interrupted by user" + Colors.RESET)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
