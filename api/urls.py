from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, MemberViewSet, borrow_book, return_book
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from djoser.views import UserViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('members', MemberViewSet)
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('borrow/', borrow_book),
    path('return/', return_book),
    path('auth/jwt/create/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
