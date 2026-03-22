import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from master_data.models import Unit

# Create Superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin / admin123")

# Create a Unit
unit, _ = Unit.objects.get_or_create(name='Main Factory')
print(f"Unit created: {unit.name}")

print("Seed data finished.")
