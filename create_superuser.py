import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@exemplo.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if not password:
    print("DJANGO_SUPERUSER_PASSWORD não configurada. Pulando criação de superusuário.")
else:
    if not User.objects.filter(username=username).exists():
        print(f"Criando superusuário: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print(f"Superusuário {username} já existe.")
