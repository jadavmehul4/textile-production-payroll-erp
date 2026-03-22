import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from master_data.models import Unit

# Create Superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

# Create a Unit
unit, _ = Unit.objects.get_or_create(name='Main Factory')

print("Seed data created.")
