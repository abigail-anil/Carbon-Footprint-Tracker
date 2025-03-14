from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    company_name = models.CharField(max_length=100, blank=True)  # Company name field
    email_verified = models.BooleanField(default=False)  # Indicates if the email is verified
    verification_token = models.CharField(max_length=255, blank=True, null=True)  # Token for email verification
    verification_token_expiry = models.DateTimeField(blank=True, null=True)  # Optional expiry for the token

    def __str__(self):
        return self.user.username  # Display the username in admin panel

