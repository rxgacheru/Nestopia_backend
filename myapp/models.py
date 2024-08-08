from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from datetime import date, timedelta
import logging
from twilio.rest import Client as TwilioClient
from django.conf import settings
from django.core.mail import send_mail




    #AUTHENICATION



class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('caretaker', 'Caretaker'),
        ('tenant', 'tenant'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

 




    #APARTMENT


class Apartment(models.Model):
    apartment_name = models.CharField(max_length=255, null=True)
    images1 = models.JSONField(null=True)
    owner_name = models.CharField(max_length=255, null=True)
    owner_contact = models.CharField(max_length=20, null=True)
    owner_email = models.EmailField( null=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    amenities_available = models.TextField(null=True)
    types_of_houses_available = models.TextField(null=True)
    number_of_buildings = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.apartment_name

class Building(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='buildings', on_delete=models.CASCADE)
    images2 = models.JSONField()
    building_name = models.CharField(max_length=255)
    number_of_floors = models.PositiveIntegerField()
    total_units = models.PositiveIntegerField()
    units_available = models.PositiveIntegerField()
    units_occupied = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.units_available + self.units_occupied > self.total_units:
            raise ValueError("Sum of available and occupied units cannot exceed total units.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Building: {self.building_name}"
    
class Floor(models.Model):
    building = models.ForeignKey(Building, related_name='floors', on_delete=models.CASCADE)
    floor_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Floor {self.floor_number} in {self.building.building_name}"

class House(models.Model):
    LISTING_TYPE_CHOICES = [
        ('bed_sitter', 'Bed Sitter'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
        ('four_bedroom', 'Four Bedroom'),
        ('five_bedroom', 'Five Bedroom'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    ]

    UNIT_LISTING = [
        ('rent', 'Rent'),
        ('sale', 'Sale'),
        ('both', 'Both'),
    ]


    images3 = models.JSONField()
    building = models.ForeignKey(Building, related_name='houses', on_delete=models.CASCADE)
    floor_number = models.ForeignKey(Floor, related_name='houses', on_delete=models.CASCADE)
    house_number = models.CharField(max_length=50)
    house_type = models.CharField(max_length=50, choices=LISTING_TYPE_CHOICES, default='one_bedroom')
    listing_type = models.CharField(max_length=10, choices=UNIT_LISTING)
    house_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.building and self.pk:
            self._meta.get_field('floor_number').choices = [(i, i) for i in range(1, self.building.number_of_floors + 1)]

    def clean(self):
        if self.listing_type == 'rent' and self.sale_price is not None:
            raise ValidationError('Sale price must be null for rental listings.')
        if self.listing_type == 'sale' and self.rent_price is not None:
            raise ValidationError('Rent price must be null for sale listings.')
        if self.listing_type == 'both' and (self.rent_price is None or self.sale_price is None):
            raise ValidationError('Both rent price and sale price must be provided for listings meant for both.')

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = House.objects.get(pk=self.pk).house_status
        
        super().save(*args, **kwargs)

        if previous_status != self.house_status:
            if self.house_status == 'occupied':
                self.building.units_occupied += 1
                self.building.units_available -= 1
            elif previous_status == 'occupied' and self.house_status == 'available':
                self.building.units_occupied -= 1
                self.building.units_available += 1
            
            self.building.save()

    def __str__(self):
        return f"House {self.house_number} - Floor {self.floor_number} - {self.listing_type.capitalize()} - Building: {self.building.building_name}"




   
    #OCCUPANTS


logger = logging.getLogger(__name__)

class Tenant(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('completed', 'Sale Completed'),
    ]

    LISTING_TYPE_CHOICES = [
        ('bed_sitter', 'Bed Sitter'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
        ('four_bedroom', 'Four Bedroom'),
        ('five_bedroom', 'Five Bedroom'),
    ]

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='tenants')
    floor_number = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='tenants')    
    house_number = models.ForeignKey(House, on_delete=models.CASCADE, related_name='tenants')
    house_type = models.CharField(max_length=50, choices=LISTING_TYPE_CHOICES, default='one_bedroom')
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()], max_length=254, blank=True)
    id_number = models.IntegerField(unique=True, null=True)
    mobile_phone = models.CharField(max_length=15, null=True)
    move_in_date = models.DateField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    last_payment_date = models.DateField(null=True, blank=True)
    rent_deficit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_days_paid = models.IntegerField(default=0)
    garbage_payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    last_garbage_payment_date = models.DateField(null=True, blank=True)
    garbage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.house.building != self.building:
            raise ValidationError('House must belong to the selected building.')

    def update_payment_status(self, amount_paid):
        if self.payment_status == 'completed':
            return

        monthly_rent = self.house.rent_price
        if monthly_rent is None:
            raise ValidationError('Rent price must be set for the house.')

        # Calculate rent due
        if self.last_payment_date:
            days_since_last_payment = (date.today() - self.last_payment_date).days
        else:
            days_since_last_payment = (date.today() - self.move_in_date).days

        rent_due = (days_since_last_payment / 30) * monthly_rent
        rent_deficit = rent_due - amount_paid

        if rent_deficit <= 0:
            self.payment_status = 'paid'
            self.advance_days_paid = int(abs(rent_deficit) / (monthly_rent / 30))
            self.rent_deficit = 0
        else:
            self.payment_status = 'unpaid'
            self.advance_days_paid = 0
            self.rent_deficit = rent_deficit

        self.last_payment_date = date.today()
        self.save()
        self.send_payment_notification()

    def update_garbage_payment_status(self, amount_paid):
        if self.garbage_payment_status == 'completed':
            return

        monthly_garbage_fee = self.garbage_fee
        if monthly_garbage_fee is None:
            raise ValidationError('Garbage fee must be set.')

        # Calculate garbage fee due
        if self.last_garbage_payment_date:
            days_since_last_payment = (date.today() - self.last_garbage_payment_date).days
        else:
            days_since_last_payment = (date.today() - self.move_in_date).days

        garbage_due = (days_since_last_payment / 30) * monthly_garbage_fee
        garbage_deficit = garbage_due - amount_paid

        if garbage_deficit <= 0:
            self.garbage_payment_status = 'paid'
            self.advance_days_paid = int(abs(garbage_deficit) / (monthly_garbage_fee / 30))
            self.garbage_deficit = 0
        else:
            self.garbage_payment_status = 'unpaid'
            self.advance_days_paid = 0
            self.garbage_deficit = garbage_deficit

        self.last_garbage_payment_date = date.today()
        self.save()
        self.send_payment_notification()

    def send_payment_notification(self):
        # Send email notification if email is provided
        if self.email:
            try:
                subject = 'Payment Status Update'
                message = (
                    f"Dear {self.name},\n\n"
                    f"Your current payment status is as follows:\n"
                    f"Rent Payment Status: {self.payment_status}\n"
                    f"Rent Deficit: {self.rent_deficit}\n"
                    f"Garbage Fee Payment Status: {self.garbage_payment_status}\n"
                    f"Garbage Deficit: {self.garbage_deficit}\n\n"
                    f"Thank you."
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
            except Exception as e:
                logger.error(f"Failed to send email to {self.email}: {str(e)}")

        # Send SMS notification if mobile phone is provided
        if self.mobile_phone:
            try:
                # Initialize Twilio client
                client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = (
                    f"Dear {self.name},\n\n"
                    f"Your payment status is as follows:\n"
                    f"Rent Payment Status: {self.payment_status}\n"
                    f"Rent Deficit: {self.rent_deficit}\n"
                    f"Garbage Fee Payment Status: {self.garbage_payment_status}\n"
                    f"Garbage Deficit: {self.garbage_deficit}\n\n"
                    f"Thank you."
                )
                client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=self.mobile_phone
                )
            except Exception as e:
                logger.error(f"Failed to send SMS to {self.mobile_phone}: {str(e)}")

    def __str__(self):
        return f"Tenant: {self.name} - House {self.house_number.house_number}"
    

    
class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartments/')

    def __str__(self):
        return f"Image for Apartment {self.apartment.apartment_name}"





#RENTALAGREEMENT
    

class RentalAgreement(models.Model):
    tenant = models.ForeignKey(Tenant, related_name='agreements', on_delete=models.CASCADE)
    house = models.ForeignKey(House, related_name='agreements', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    agreement_status = models.CharField(max_length=20, choices=[('active', 'Active'), ('terminated', 'Terminated')], default='active')

    def __str__(self):
        return f"Agreement for {self.tenant.name} - House {self.house.house_number}"





     #MAINTENANCE   
    

class MaintenanceRequest(models.Model):
    house = models.ForeignKey(House, related_name='maintenance_requests', on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Maintenance Request for House {self.house.house_number} - Status: {self.status}"