from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from library.models import Book, Member, BorrowRecord
from .serializers import BookSerializer, MemberSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

@api_view(['POST'])
def borrow_book(request):
    book = Book.objects.get(id=request.data['book'])
    member = Member.objects.get(id=request.data['member'])

    if not book.is_available:
        return Response({"error": "Book not available"}, status=400)

    BorrowRecord.objects.create(book=book, member=member)
    book.is_available = False
    book.save()

    return Response({"message": "Book borrowed successfully"})

@api_view(['POST'])
def return_book(request):
    record = BorrowRecord.objects.get(
        book_id=request.data['book'],
        member_id=request.data['member'],
        return_date__isnull=True
    )

    record.return_date = timezone.now()
    record.save()

    record.book.is_available = True
    record.book.save()

    return Response({"message": "Book returned successfully"})
