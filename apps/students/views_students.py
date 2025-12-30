"""
Funciones para gestión de estudiantes, planes y suscripciones
"""
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template import loader
from http import HTTPStatus
from datetime import datetime, timedelta
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback si dateutil no está instalado
    def relativedelta(date1, date2):
        return type('obj', (object,), {'years': (date1 - date2).days // 365})()

from apps.sales.models import Student, Cycle, Enrollment
from apps.hrm.models import Subsidiary
from apps.users.models import CustomUser
from decimal import Decimal
import decimal
from django.db.models import Q


# =============================================================================
# FUNCIONES PARA ESTUDIANTES
# =============================================================================



