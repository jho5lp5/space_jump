"""
Vistas para reportes de texto/tablas de la academia
"""
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from http import HTTPStatus
from datetime import datetime
from decimal import Decimal

from .models import CashFlow
from ..hrm.models import Subsidiary
from ..students.models import Enrollment, Student, Cycle, TrainingSchedule, TimeSlot


def reports_list(request):
    """Vista principal para reportes de texto/tablas"""
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        
        # Obtener la sucursal del usuario actual
        user_subsidiary = None
        if hasattr(request.user, 'subsidiary') and request.user.subsidiary:
            user_subsidiary = request.user.subsidiary
        
        # Fecha actual para el filtro
        current_date = datetime.now()
        current_month = current_date.strftime('%Y-%m')
        
        return render(request, 'accounting/reports_list.html', {
            'subsidiary_set': subsidiary_set,
            'user_subsidiary': user_subsidiary,
            'current_month': current_month,
        })


@csrf_exempt
def get_enrollments_report(request):
    """Obtener reporte de inscripciones en formato tabla"""
    if request.method == 'POST':
        try:
            # Obtener parámetros del filtro
            report_month = request.POST.get('report_month')
            subsidiary_id = request.POST.get('subsidiary')
            
            if not report_month:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar un mes'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Convertir mes a rango de fechas
            year, month = report_month.split('-')
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date()
            
            # Filtrar inscripciones
            enrollments_filter = {}
            subsidiary_obj = None
            
            if subsidiary_id and subsidiary_id != '0':
                subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
                enrollments_filter = {'subsidiary_id': subsidiary_id}
            
            enrollments = Enrollment.objects.filter(
                enrollment_date__gte=start_date,
                enrollment_date__lt=end_date,
                **enrollments_filter
            ).select_related(
                'student', 'cycle', 'schedule', 'time_slot', 'time_slot__teacher', 'subsidiary', 'user'
            ).order_by('enrollment_date', 'student__full_name')
            
            # Calcular totales
            total_price = enrollments.aggregate(Sum('price'))['price__sum'] or Decimal('0')
            total_advance = enrollments.aggregate(Sum('advance'))['advance__sum'] or Decimal('0')
            total_remaining = enrollments.aggregate(Sum('remaining'))['remaining__sum'] or Decimal('0')
            
            # Preparar datos para la tabla
            enrollments_data = []
            for idx, enrollment in enumerate(enrollments, 1):
                teacher_name = '-'
                if enrollment.time_slot.teacher:
                    teacher_name = f"{enrollment.time_slot.teacher.first_name or ''} {enrollment.time_slot.teacher.last_name or ''}".strip() or enrollment.time_slot.teacher.username
                
                time_slot_str = f"{enrollment.time_slot.start_time.strftime('%H:%M')} - {enrollment.time_slot.end_time.strftime('%H:%M')}"
                if enrollment.time_slot.age_description:
                    time_slot_str += f" ({enrollment.time_slot.age_description})"
                
                enrollments_data.append({
                    'num': idx,
                    'date': enrollment.enrollment_date.strftime('%d/%m/%Y'),
                    'student': enrollment.student.full_name or '-',
                    'dni': enrollment.student.document_number or '-',
                    'cycle': enrollment.cycle.name,
                    'schedule': enrollment.schedule.name,
                    'timeslot': time_slot_str,
                    'teacher': teacher_name,
                    'subsidiary': enrollment.subsidiary.name if enrollment.subsidiary else '-',
                    'price': float(enrollment.price),
                    'advance': float(enrollment.advance),
                    'remaining': float(enrollment.remaining),
                })
            
            return JsonResponse({
                'success': True,
                'enrollments': enrollments_data,
                'totals': {
                    'count': enrollments.count(),
                    'total_price': float(total_price),
                    'total_advance': float(total_advance),
                    'total_remaining': float(total_remaining),
                },
                'subsidiary': subsidiary_obj.name if subsidiary_obj else 'Todas las sucursales',
                'month_name': start_date.strftime('%B %Y').capitalize()
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'message': f'Error al generar reporte: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def get_students_report(request):
    """Obtener reporte de deportistas en formato tabla"""
    if request.method == 'POST':
        try:
            subsidiary_id = request.POST.get('subsidiary', '0')
            
            # Filtrar estudiantes
            students_filter = {'is_active': True}
            subsidiary_obj = None
            
            if subsidiary_id and subsidiary_id != '0':
                subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
                students_filter['subsidiary_id'] = subsidiary_id
            
            students = Student.objects.filter(**students_filter).order_by('full_name', 'surname')
            
            # Preparar datos para la tabla
            students_data = []
            for idx, student in enumerate(students, 1):
                parent_name = f"{student.parent_first_name or ''} {student.parent_surname or ''}".strip() or '-'
                
                students_data.append({
                    'num': idx,
                    'full_name': student.full_name or '-',
                    'dni': student.document_number or '-',
                    'birth_date': student.birth_date.strftime('%d/%m/%Y') if student.birth_date else '-',
                    'age': student.current_age or '-',
                    'phone': student.phone or '-',
                    'parent_name': parent_name,
                    'parent_phone': student.parent_phone or '-',
                    'subsidiary': student.subsidiary.name if student.subsidiary else '-',
                    'creation_date': student.creation_date.strftime('%d/%m/%Y %H:%M') if student.creation_date else '-',
                })
            
            return JsonResponse({
                'success': True,
                'students': students_data,
                'total': students.count(),
                'subsidiary': subsidiary_obj.name if subsidiary_obj else 'Todas las sucursales',
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'message': f'Error al generar reporte: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def get_pending_payments_report(request):
    """Obtener reporte de pagos pendientes en formato tabla"""
    if request.method == 'POST':
        try:
            subsidiary_id = request.POST.get('subsidiary', '0')
            
            # Filtrar inscripciones con pagos pendientes
            enrollments_filter = {'remaining__gt': 0}
            subsidiary_obj = None
            
            if subsidiary_id and subsidiary_id != '0':
                subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
                enrollments_filter['subsidiary_id'] = subsidiary_id
            
            enrollments = Enrollment.objects.filter(**enrollments_filter).select_related(
                'student', 'cycle', 'schedule', 'time_slot', 'subsidiary'
            ).order_by('enrollment_date')
            
            # Calcular totales
            total_price = enrollments.aggregate(Sum('price'))['price__sum'] or Decimal('0')
            total_advance = enrollments.aggregate(Sum('advance'))['advance__sum'] or Decimal('0')
            total_remaining = enrollments.aggregate(Sum('remaining'))['remaining__sum'] or Decimal('0')
            
            # Preparar datos para la tabla
            today = datetime.now().date()
            enrollments_data = []
            for idx, enrollment in enumerate(enrollments, 1):
                days_pending = (today - enrollment.enrollment_date).days
                
                enrollments_data.append({
                    'num': idx,
                    'date': enrollment.enrollment_date.strftime('%d/%m/%Y'),
                    'student': enrollment.student.full_name or '-',
                    'dni': enrollment.student.document_number or '-',
                    'cycle': enrollment.cycle.name,
                    'price': float(enrollment.price),
                    'advance': float(enrollment.advance),
                    'remaining': float(enrollment.remaining),
                    'subsidiary': enrollment.subsidiary.name if enrollment.subsidiary else '-',
                    'days_pending': days_pending,
                })
            
            return JsonResponse({
                'success': True,
                'enrollments': enrollments_data,
                'totals': {
                    'count': enrollments.count(),
                    'total_price': float(total_price),
                    'total_advance': float(total_advance),
                    'total_remaining': float(total_remaining),
                },
                'subsidiary': subsidiary_obj.name if subsidiary_obj else 'Todas las sucursales',
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'message': f'Error al generar reporte: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)

