from django.shortcuts import render
from .models import Genotipo
import datetime

def dashboard_passaportes(request):
    """Dashboard público com passaportes autorizados"""
    selecoes = Genotipo.objects.filter(tipo='SELECAO', publicar_passaporte=True, status='ATIVO')
    cultivares = Genotipo.objects.filter(tipo='CULTIVAR', publicar_passaporte=True, status='ATIVO')
    mutantes = Genotipo.objects.filter(tipo='MUTANTE', publicar_passaporte=True, status='ATIVO')
    
    context = {
        'selecoes': selecoes,
        'cultivares': cultivares,
        'mutantes': mutantes,
        'year': datetime.datetime.now().year,
    }
    return render(request, 'dashboard_passaportes.html', context)