from django.urls import path
from .views import *
from. import views


urlpatterns = [

        #AUTHENTICATION
  
    path('api/register/', UserListCreateView.as_view(), name='register'),
    path('api/login/', login_view, name='login'),
    path('api/login/', views.ObtainTokenPairWithRoleView.as_view(), name="token_obtain_pair"),
    path('api/login/<int:pk>/', views.ObtainTokenPairWithRoleView.as_view(), name="token_obtain_pair"),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),


        #DASHBOARDS

    path('api/me/', UserDetailView.as_view(), name='user_detail'),
    path('api/admin/users/', AdminUserManagementView.as_view(), name='admin_user_management'),
    path('api/admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('api/landlord/dashboard/', LandlordDashboardView.as_view(), name='landlord_dashboard'),
    path('api/caretaker/dashboard/', CaretakerDashboardView.as_view(), name='caretaker_dashboard'),
    path('api/tenant/dashboard/', TenantDashboardView.as_view(), name='tenant_dashboard'),
    path('api/user/dashboard/', UserDashboardView.as_view(), name='user_dashboard'),


        #APARTMENTS

     path('apartments/', ApartmentAPIView.as_view(), name='apartment-list'),
    path('apartments/<int:pk>/', ApartmentDetailAPIView.as_view(), name='apartment-detail'),
    
    path('buildings/', BuildingAPIView.as_view(), name='building-list'),
    path('buildings/<int:pk>/', BuildingDetailAPIView.as_view(), name='building-detail'),

    path('floors/', FloorAPIView.as_view(), name='floor-list'),
    path('floors/<int:pk>/', FloorDetailAPIView.as_view(), name='floor-detail'),

    path('houses/', HouseAPIView.as_view(), name='house-list'),
    path('houses/<int:pk>/', HouseDetailAPIView.as_view(), name='house-detail'),

    path('tenants/', TenantAPIView.as_view(), name='tenant-list'),
    path('tenants/<int:pk>/', TenantDetailAPIView.as_view(), name='tenant-detail'),

    path('apartment-images/', ApartmentImageAPIView.as_view(), name='apartmentimage-list'),
    path('apartment-images/<int:pk>/', ApartmentImageDetailAPIView.as_view(), name='apartmentimage-detail'),

    path('rental-agreements/', RentalAgreementAPIView.as_view(), name='rentalagreement-list'),
    path('rental-agreements/<int:pk>/', RentalAgreementDetailAPIView.as_view(), name='rentalagreement-detail'),

    path('maintenance-requests/', MaintenanceRequestAPIView.as_view(), name='maintenancerequest-list'),
    path('maintenance-requests/<int:pk>/', MaintenanceRequestDetailAPIView.as_view(), name='maintenancerequest-detail'),
]


