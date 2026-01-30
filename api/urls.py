from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, MemberViewSet, borrow_book, return_book

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('members', MemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('borrow/', borrow_book),
    path('return/', return_book),
]
