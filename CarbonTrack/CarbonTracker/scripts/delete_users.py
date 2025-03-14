import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CarbonTrack.settings')  # Replace 'CarbonTrack' with your project name
django.setup()

from django.contrib.auth.models import User

try:
    User.objects.filter(is_superuser=False).delete()
    print("Non-superusers deleted successfully.")
except Exception as e:
    print(f"An error occurred: {e}")