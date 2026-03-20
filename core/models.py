from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='passenger')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Edge(models.Model):
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')

    class Meta:
        unique_together = ('from_node', 'to_node')

    def __str__(self):
        return f"{self.from_node} -> {self.to_node}"


class Trip(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    start_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='trip_starts')
    end_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='trip_ends')
    route = models.JSONField(default=list)
    visited_nodes = models.JSONField(default=list)
    current_node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_trips')
    max_passengers = models.IntegerField(default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip by {self.driver.username}: {self.start_node} -> {self.end_node}"


class CarpoolRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carpool_requests')
    pickup_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='pickups')
    dropoff_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='dropoffs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.passenger.username}: {self.pickup_node} -> {self.dropoff_node}"


class CarpoolOffer(models.Model):
    STATUS_CHOICES = (
        ('offered', 'Offered'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='offers')
    request = models.ForeignKey(CarpoolRequest, on_delete=models.CASCADE, related_name='offers')
    detour = models.IntegerField(default=0)
    fare = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offered')

    def __str__(self):
        return f"Offer from {self.trip.driver.username} to {self.request.passenger.username}"
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username}'s wallet - ${self.balance}"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('topup', 'Top Up'),
        ('fare_deduction', 'Fare Deduction'),
        ('driver_earning', 'Driver Earning'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField()
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"