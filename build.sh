#!/usr/bin/env bash
# Sair em caso de erro
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Rodar migrações
python manage.py migrate

# Criar superusuário automaticamente
python create_superuser.py
