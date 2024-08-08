from rest_framework import generics, status, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_str
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from corsheaders.middleware import CorsMiddleware
from .models import *
from .serializers import *


from .models import *
from .serializers import *
from .permissions import *

User = get_user_model()

class CorsMiddleware(CorsMiddleware):
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response




  #AUTHENICATION
    

    
class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

class ObtainTokenPairWithRoleView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role
        })

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
                return redirect('login')  # Redirect to login page after successful password reset
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('password_reset')  
    
@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   

   #DASHBOARDS



class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({'message': 'Welcome to the admin dashboard'})

class LandlordDashboardView(APIView):
    permission_classes = [IsLandlord]

    def get(self, request):
        return Response({'message': 'Welcome to the landlord dashboard'})

class CaretakerDashboardView(APIView):
    permission_classes = [IsCaretaker]

    def get(self, request):
        return Response({'message': 'Welcome to the caretaker dashboard'})

class TenantDashboardView(APIView):
    permission_classes = [IsTenant]

    def get(self, request):
        return Response({'message': 'Welcome to the tenant dashboard'})

class UserDashboardView(APIView):
    permission_classes = [IsUser]

    def get(self, request):
        return Response({'message': 'Welcome to the user dashboard'})
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class AdminUserManagementView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]


   
  #APARTMENTS




class ApartmentAPIView(APIView):
    def get(self, request):
        apartments = Apartment.objects.all()
        serializer = ApartmentSerializer(apartments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApartmentDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Apartment.objects.get(pk=pk)
        except Apartment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        apartment = self.get_object(pk)
        serializer = ApartmentSerializer(apartment)
        return Response(serializer.data)

    def put(self, request, pk):
        apartment = self.get_object(pk)
        serializer = ApartmentSerializer(apartment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        apartment = self.get_object(pk)
        apartment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ApartmentImageAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            image = get_object_or_404(ApartmentImage, pk=pk)
            serializer = ApartmentImageSerializer(image)
        else:
            images = ApartmentImage.objects.all()
            serializer = ApartmentImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApartmentImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        image = get_object_or_404(ApartmentImage, pk=pk)
        serializer = ApartmentImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        image = get_object_or_404(ApartmentImage, pk=pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BuildingAPIView(APIView):
    def get(self, request):
        buildings = Building.objects.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BuildingDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Building.objects.get(pk=pk)
        except Building.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        building = self.get_object(pk)
        serializer = BuildingSerializer(building)
        return Response(serializer.data)

    def put(self, request, pk):
        building = self.get_object(pk)
        serializer = BuildingSerializer(building, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        building = self.get_object(pk)
        building.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FloorAPIView(APIView):
    def get(self, request):
        floors = Floor.objects.all()
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FloorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FloorDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Floor.objects.get(pk=pk)
        except Floor.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        floor = self.get_object(pk)
        serializer = FloorSerializer(floor)
        return Response(serializer.data)

    def put(self, request, pk):
        floor = self.get_object(pk)
        serializer = FloorSerializer(floor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        floor = self.get_object(pk)
        floor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class HouseAPIView(APIView):
    def get(self, request):
        houses = House.objects.all()
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HouseDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return House.objects.get(pk=pk)
        except House.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        house = self.get_object(pk)
        serializer = HouseSerializer(house)
        return Response(serializer.data)

    def put(self, request, pk):
        house = self.get_object(pk)
        serializer = HouseSerializer(house, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        house = self.get_object(pk)
        house.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TenantAPIView(APIView):
    def get(self, request):
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TenantDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        tenant = self.get_object(pk)
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

    def put(self, request, pk):
        tenant = self.get_object(pk)
        serializer = TenantSerializer(tenant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tenant = self.get_object(pk)
        tenant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ApartmentImageAPIView(APIView):
    def get(self, request):
        apartment_images = ApartmentImage.objects.all()
       
class ApartmentImageDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return ApartmentImage.objects.get(pk=pk)
        except ApartmentImage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        apartment_image = self.get_object(pk)
        serializer = ApartmentImageSerializer(apartment_image)
        return Response(serializer.data)

    def put(self, request, pk):
        apartment_image = self.get_object(pk)
        serializer = ApartmentImageSerializer(apartment_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        apartment_image = self.get_object(pk)
        apartment_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RentalAgreementAPIView(APIView):
    def get(self, request):
        rental_agreements = RentalAgreement.objects.all()
        serializer = RentalAgreementSerializer(rental_agreements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RentalAgreementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RentalAgreementDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return RentalAgreement.objects.get(pk=pk)
        except RentalAgreement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rental_agreement = self.get_object(pk)
        serializer = RentalAgreementSerializer(rental_agreement)
        return Response(serializer.data)

    def put(self, request, pk):
        rental_agreement = self.get_object(pk)
        serializer = RentalAgreementSerializer(rental_agreement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rental_agreement = self.get_object(pk)
        rental_agreement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MaintenanceRequestAPIView(APIView):
    def get(self, request):
        maintenance_requests = MaintenanceRequest.objects.all()
        serializer = MaintenanceRequestSerializer(maintenance_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaintenanceRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MaintenanceRequestAPIView(APIView):
    def get(self, request):
        maintenance_requests = MaintenanceRequest.objects.all()
        serializer = MaintenanceRequestSerializer(maintenance_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaintenanceRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MaintenanceRequestDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return MaintenanceRequest.objects.get(pk=pk)
        except MaintenanceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        maintenance_request = self.get_object(pk)
        serializer = MaintenanceRequestSerializer(maintenance_request)
        return Response(serializer.data)

    def put(self, request, pk):
        maintenance_request = self.get_object(pk)
        serializer = MaintenanceRequestSerializer(maintenance_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        maintenance_request = self.get_object(pk)
        maintenance_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)