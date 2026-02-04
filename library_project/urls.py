from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/ReDoc Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="Library REST API",
        default_version='v1',
        description="""
        A comprehensive REST API for managing a library system with authentication and role-based permissions.
        
        **Features:**
        - User authentication with JWT tokens
        - Role-based access control (Librarians and Members)
        - Book management (CRUD operations)
        - Member management
        - Book borrowing and returning system
        
        **Authentication:**
        Use the JWT endpoints to get access and refresh tokens. Include the access token in the Authorization header as: Bearer <token>
        """,
        contact=openapi.Contact(email="library@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API endpoints
    path('api/', include('api.urls')),
    
    # Swagger/ReDoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]
