from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from http import HTTPStatus

import pytz
import json
from decimal import Decimal
from django.template import loader
from datetime import datetime, date
from django.db.models import Sum, Q
from django.db.models import Count
from .views_API import query_apis_net_dni_ruc
from ..hrm.models import Subsidiary
from ..users.models import CustomUser



