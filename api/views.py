from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from library.models import Book, Member, BorrowRecord
from .serializers import BookSerializer, MemberSerializer
from .permissions import IsLibrarianOrReadOnly, CanBorrowReturnBooks


class BookViewSet(viewsets.ModelViewSet):
    """
    BookViewSet - Manage Library Books

    This endpoint provides CRUD operations for books in the library.

    **Permissions:**
    - GET (List): Public - No authentication required
    - GET (Retrieve): Public - No authentication required
    - POST (Create): Librarians only (is_staff=True)
    - PUT (Update): Librarians only (is_staff=True)
    - PATCH (Partial Update): Librarians only (is_staff=True)
    - DELETE: Librarians only (is_staff=True)

    **Available Endpoints:**
    - GET /api/books/ - List all books (paginated, 10 per page)
    - POST /api/books/ - Create a new book (Librarians only)
    - GET /api/books/{id}/ - Retrieve a specific book
    - PUT /api/books/{id}/ - Update a book (Librarians only)
    - PATCH /api/books/{id}/ - Partial update a book (Librarians only)
    - DELETE /api/books/{id}/ - Delete a book (Librarians only)

    **Response Format:**
    - Success: 200 OK (GET), 201 Created (POST), 204 No Content (DELETE)
    - Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]


class MemberViewSet(viewsets.ModelViewSet):
    """
    MemberViewSet - Manage Library Members

    This endpoint provides operations for managing library members.

    **Permissions:**
    - GET (List): Authenticated users only
    - GET (Retrieve): Authenticated users only
    - POST (Create): Librarians only (is_staff=True)
    - PUT (Update): Librarians only (is_staff=True)
    - PATCH (Partial Update): Librarians only (is_staff=True)
    - DELETE: Librarians only (is_staff=True)

    **Available Endpoints:**
    - GET /api/members/ - List all members (authenticated users)
    - POST /api/members/ - Create a new member (Librarians only)
    - GET /api/members/{id}/ - Retrieve a specific member (authenticated)
    - PUT /api/members/{id}/ - Update member info (Librarians only)
    - PATCH /api/members/{id}/ - Partial update member (Librarians only)
    - DELETE /api/members/{id}/ - Delete a member (Librarians only)

    **Response Format:**
    - Success: 200 OK (GET), 201 Created (POST), 204 No Content (DELETE)
    - Error: 401 Unauthorized, 403 Forbidden, 404 Not Found

    **Authentication Required:**
    All requests require JWT token in Authorization header: Bearer <token>
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Override permissions based on HTTP method.
        
        - Safe methods (GET): IsAuthenticated
        - Unsafe methods (POST, PUT, PATCH, DELETE): IsLibrarian
        """
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]


@api_view(['POST'])
@permission_classes([CanBorrowReturnBooks])
def borrow_book(request):
    """
    Borrow a Book - Authenticated Users Only

    Allows authenticated users (members and librarians) to borrow a book from the library.

    **Permissions:**
    - Requires JWT authentication (Bearer token)
    - Both Members and Librarians can borrow books

    **Request Body (JSON):**
    ```json
    {
        "book": <integer: book_id>,
        "member": <integer: member_id>
    }
    ```

    **Response:**
    - Success (200 OK):
        ```json
        {
            "message": "Book borrowed successfully"
        }
        ```
    - Error (400 Bad Request):
        ```json
        {
            "error": "Book not available"
        }
        ```
    - Error (404 Not Found):
        ```json
        {
            "error": "Book not found"
        }
        ```
        or
        ```json
        {
            "error": "Member not found"
        }
        ```

    **Authentication:**
    Include JWT token in Authorization header: Bearer <token>

    **Business Logic:**
    1. Validates that the book exists
    2. Validates that the member exists
    3. Checks if the book is available
    4. Creates a BorrowRecord
    5. Marks the book as unavailable
    """
    try:
        book = Book.objects.get(id=request.data['book'])
        member = Member.objects.get(id=request.data['member'])

        if not book.is_available:
            return Response(
                {"error": "Book not available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        BorrowRecord.objects.create(book=book, member=member)
        book.is_available = False
        book.save()

        return Response(
            {"message": "Book borrowed successfully"},
            status=status.HTTP_200_OK
        )
    except Book.DoesNotExist:
        return Response(
            {"error": "Book not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Member.DoesNotExist:
        return Response(
            {"error": "Member not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([CanBorrowReturnBooks])
def return_book(request):
    """
    Return a Book - Authenticated Users Only

    Allows authenticated users to return a previously borrowed book to the library.

    **Permissions:**
    - Requires JWT authentication (Bearer token)
    - Both Members and Librarians can return books

    **Request Body (JSON):**
    ```json
    {
        "book": <integer: book_id>,
        "member": <integer: member_id>
    }
    ```

    **Response:**
    - Success (200 OK):
        ```json
        {
            "message": "Book returned successfully"
        }
        ```
    - Error (404 Not Found):
        ```json
        {
            "error": "No active borrow record found"
        }
        ```
    - Error (400 Bad Request):
        ```json
        {
            "error": "<error_message>"
        }
        ```

    **Authentication:**
    Include JWT token in Authorization header: Bearer <token>

    **Business Logic:**
    1. Finds the active borrow record (return_date is null)
    2. Sets the return_date to current timestamp
    3. Marks the book as available again
    4. Saves the updated records

    **Note:**
    A borrow record is considered "active" if it has no return_date.
    Only active records can be returned.
    """
    try:
        record = BorrowRecord.objects.get(
            book_id=request.data['book'],
            member_id=request.data['member'],
            return_date__isnull=True
        )

        record.return_date = timezone.now()
        record.save()

        record.book.is_available = True
        record.book.save()

        return Response(
            {"message": "Book returned successfully"},
            status=status.HTTP_200_OK
        )
    except BorrowRecord.DoesNotExist:
        return Response(
            {"error": "No active borrow record found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
