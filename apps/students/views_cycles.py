"""
Vistas para gestión de Ciclos, TrainingSchedule, TimeSlot y Enrollment
"""
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template import loader
from http import HTTPStatus
from datetime import datetime
from decimal import Decimal

from apps.students.models import Cycle, TrainingSchedule, TimeSlot, Enrollment, Student
from apps.hrm.models import Subsidiary


# =============================================================================
# CICLOS (Cycle)
# =============================================================================

def get_cycle_list(request):
    """Lista de ciclos con sus schedules y time slots"""
    cycles = Cycle.objects.prefetch_related(
        'schedules__time_slots__teacher'
    ).filter(is_active=True).order_by('-creation_date')
    return render(request, 'cycles/cycle_list.html', {'cycles': cycles})


def modal_cycle_create(request):
    """Modal para crear ciclo"""
    t = loader.get_template('cycles/cycle_create.html')
    return JsonResponse({'form': t.render({}, request)})


@csrf_exempt
def save_cycle(request):
    """Guardar nuevo ciclo"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            duration_months = request.POST.get('duration_months', '1')
            start_date_str = request.POST.get('start_date', '')
            end_date_str = request.POST.get('end_date', '')
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre del ciclo es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            start_date = None
            end_date = None
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            cycle = Cycle.objects.create(
                name=name.upper(),
                duration_months=int(duration_months),
                start_date=start_date,
                end_date=end_date,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ciclo creado exitosamente',
                'cycle_id': cycle.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear el ciclo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


def modal_cycle_update(request):
    """Modal para actualizar ciclo"""
    pk = request.GET.get('pk', '')
    cycle_obj = None
    if pk:
        try:
            cycle_obj = Cycle.objects.get(id=int(pk))
        except Cycle.DoesNotExist:
            pass
    
    t = loader.get_template('cycles/cycle_update.html')
    return JsonResponse({'form': t.render({'cycle_obj': cycle_obj}, request)})


@csrf_exempt
def update_cycle(request):
    """Actualizar ciclo"""
    if request.method == 'POST':
        try:
            cycle_id = request.POST.get('cycle_id', '')
            if not cycle_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de ciclo es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cycle = Cycle.objects.get(id=int(cycle_id))
            cycle.name = request.POST.get('name', cycle.name).upper()
            cycle.duration_months = int(request.POST.get('duration_months', cycle.duration_months))
            
            start_date_str = request.POST.get('start_date', '')
            end_date_str = request.POST.get('end_date', '')
            if start_date_str:
                cycle.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str:
                cycle.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            cycle.is_active = request.POST.get('is_active', 'true') == 'true'
            cycle.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Ciclo actualizado exitosamente'
            })
            
        except Cycle.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Ciclo no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# TRAINING SCHEDULE (Horarios de Entrenamiento)
# =============================================================================

def modal_schedule_create(request):
    """Modal para crear schedule"""
    cycle_id = request.GET.get('cycle_id', '')
    cycle_obj = None
    if cycle_id:
        try:
            cycle_obj = Cycle.objects.get(id=int(cycle_id))
        except Cycle.DoesNotExist:
            pass
    
    t = loader.get_template('sales/../../templates/cycles/schedule_create.html')
    return JsonResponse({'form': t.render({'cycle_obj': cycle_obj}, request)})


@csrf_exempt
def save_schedule(request):
    """Guardar nuevo schedule"""
    if request.method == 'POST':
        try:
            cycle_id = request.POST.get('cycle_id', '')
            name = request.POST.get('name', '').strip()
            price = request.POST.get('price', '0')
            
            monday = request.POST.get('monday') == 'on'
            tuesday = request.POST.get('tuesday') == 'on'
            wednesday = request.POST.get('wednesday') == 'on'
            thursday = request.POST.get('thursday') == 'on'
            friday = request.POST.get('friday') == 'on'
            saturday = request.POST.get('saturday') == 'on'
            
            if not cycle_id or not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El ciclo y nombre son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cycle = Cycle.objects.get(id=int(cycle_id))
            
            schedule = TrainingSchedule.objects.create(
                cycle=cycle,
                name=name.upper(),
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                price=Decimal(price) if price else Decimal('0'),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Horario creado exitosamente',
                'schedule_id': schedule.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


def modal_schedule_update(request):
    """Modal para actualizar schedule"""
    pk = request.GET.get('pk', '')
    schedule_obj = None
    if pk:
        try:
            schedule_obj = TrainingSchedule.objects.select_related('cycle').get(id=int(pk))
        except TrainingSchedule.DoesNotExist:
            pass
    
    t = loader.get_template('sales/../../templates/cycles/schedule_update.html')
    return JsonResponse({'form': t.render({'schedule_obj': schedule_obj}, request)})


@csrf_exempt
def update_schedule(request):
    """Actualizar schedule"""
    if request.method == 'POST':
        try:
            schedule_id = request.POST.get('schedule_id', '')
            if not schedule_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            schedule = TrainingSchedule.objects.get(id=int(schedule_id))
            schedule.name = request.POST.get('name', schedule.name).upper()
            schedule.price = Decimal(request.POST.get('price', schedule.price))
            schedule.monday = request.POST.get('monday') == 'on'
            schedule.tuesday = request.POST.get('tuesday') == 'on'
            schedule.wednesday = request.POST.get('wednesday') == 'on'
            schedule.thursday = request.POST.get('thursday') == 'on'
            schedule.friday = request.POST.get('friday') == 'on'
            schedule.saturday = request.POST.get('saturday') == 'on'
            schedule.is_active = request.POST.get('is_active', 'true') == 'true'
            schedule.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Horario actualizado exitosamente'
            })
            
        except TrainingSchedule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Horario no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# TIME SLOT (Turnos)
# =============================================================================

def modal_timeslot_create(request):
    """Modal para crear time slot"""
    from apps.users.models import CustomUser
    
    schedule_id = request.GET.get('schedule_id', '')
    schedule_obj = None
    if schedule_id:
        try:
            schedule_obj = TrainingSchedule.objects.select_related('cycle').get(id=int(schedule_id))
        except TrainingSchedule.DoesNotExist:
            pass
    
    # Obtener lista de profesores
    teachers = CustomUser.objects.filter(type_employee='2', is_active=True).order_by('first_name', 'last_name')
    
    t = loader.get_template('cycles/timeslot_create.html')
    return JsonResponse({'form': t.render({
        'schedule_obj': schedule_obj,
        'teachers': teachers
    }, request)})


@csrf_exempt
def save_timeslot(request):
    """Guardar nuevo time slot"""
    if request.method == 'POST':
        try:
            schedule_id = request.POST.get('schedule_id', '')
            start_time = request.POST.get('start_time', '')
            end_time = request.POST.get('end_time', '')
            age_description = request.POST.get('age_description', '')
            capacity = request.POST.get('capacity', '20')
            
            if not schedule_id or not start_time or not end_time:
                return JsonResponse({
                    'success': False,
                    'message': 'Horario, hora inicio y hora fin son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)
            
            schedule = TrainingSchedule.objects.get(id=int(schedule_id))
            
            teacher_id = request.POST.get('teacher_id', '')
            teacher = None
            if teacher_id:
                from apps.users.models import CustomUser
                try:
                    teacher = CustomUser.objects.get(id=int(teacher_id), type_employee='2')
                except CustomUser.DoesNotExist:
                    pass
            
            timeslot = TimeSlot.objects.create(
                schedule=schedule,
                start_time=start_time,
                end_time=end_time,
                age_description=age_description.upper() if age_description else '',
                capacity=int(capacity) if capacity else 20,
                teacher=teacher,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Turno creado exitosamente',
                'timeslot_id': timeslot.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


def modal_timeslot_update(request):
    """Modal para actualizar time slot"""
    from apps.users.models import CustomUser
    
    pk = request.GET.get('pk', '')
    timeslot_obj = None
    if pk:
        try:
            timeslot_obj = TimeSlot.objects.select_related('schedule__cycle', 'teacher').get(id=int(pk))
        except TimeSlot.DoesNotExist:
            pass
    
    # Obtener lista de profesores
    teachers = CustomUser.objects.filter(type_employee='2', is_active=True).order_by('first_name', 'last_name')
    
    t = loader.get_template('cycles/timeslot_update.html')
    return JsonResponse({'form': t.render({
        'timeslot_obj': timeslot_obj,
        'teachers': teachers
    }, request)})


@csrf_exempt
def update_timeslot(request):
    """Actualizar time slot"""
    if request.method == 'POST':
        try:
            timeslot_id = request.POST.get('timeslot_id', '')
            if not timeslot_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            timeslot = TimeSlot.objects.get(id=int(timeslot_id))
            timeslot.start_time = request.POST.get('start_time', timeslot.start_time)
            timeslot.end_time = request.POST.get('end_time', timeslot.end_time)
            timeslot.age_description = request.POST.get('age_description', '').upper()
            timeslot.capacity = int(request.POST.get('capacity', timeslot.capacity))
            timeslot.is_active = request.POST.get('is_active', 'true') == 'true'
            
            # Actualizar profesor
            teacher_id = request.POST.get('teacher_id', '')
            if teacher_id:
                from apps.users.models import CustomUser
                try:
                    timeslot.teacher = CustomUser.objects.get(id=int(teacher_id), type_employee='2')
                except CustomUser.DoesNotExist:
                    timeslot.teacher = None
            else:
                timeslot.teacher = None
            
            timeslot.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Turno actualizado exitosamente'
            })
            
        except TimeSlot.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Turno no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# ENROLLMENT (Inscripciones)
# =============================================================================

def get_enrollment_list(request):
    """Lista de inscripciones"""
    from apps.users.models import CustomUser
    
    enrollments = Enrollment.objects.select_related(
        'student', 'cycle', 'schedule', 'time_slot', 'time_slot__teacher', 'subsidiary'
    ).order_by('-enrollment_date', '-creation_date')
    
    cycles = Cycle.objects.filter(is_active=True)
    subsidiaries = Subsidiary.objects.all()
    teachers = CustomUser.objects.filter(type_employee='2', is_active=True).order_by('first_name', 'last_name')
    
    return render(request, 'enrollment/enrollment_list.html', {
        'enrollments': enrollments,
        'cycles': cycles,
        'subsidiaries': subsidiaries,
        'teachers': teachers,
    })


def modal_enrollment_create(request):
    """Modal para crear inscripción"""
    cycles = Cycle.objects.filter(is_active=True).prefetch_related('schedules__time_slots')
    subsidiaries = Subsidiary.objects.all()
    
    t = loader.get_template('enrollment/enrollment_create.html')
    return JsonResponse({'form': t.render({
        'cycles': cycles,
        'subsidiaries': subsidiaries,
    }, request)})


@csrf_exempt
def save_enrollment(request):
    """Guardar nueva inscripción"""
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id', '')
            cycle_id = request.POST.get('cycle_id', '')
            schedule_id = request.POST.get('schedule_id', '')
            timeslot_id = request.POST.get('timeslot_id', '')
            enrollment_date_str = request.POST.get('enrollment_date', '')
            price = request.POST.get('price', '0')
            advance = request.POST.get('advance', '0')
            remaining = request.POST.get('remaining', '0')
            payment_method = request.POST.get('payment_method', 'E')
            subsidiary_id = request.POST.get('subsidiary_id', '')
            observations = request.POST.get('observations', '')
            
            if not all([student_id, cycle_id, schedule_id, timeslot_id]):
                return JsonResponse({
                    'success': False,
                    'message': 'Deportista, ciclo, horario y turno son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)
            
            student = Student.objects.get(id=int(student_id))
            cycle = Cycle.objects.get(id=int(cycle_id))
            schedule = TrainingSchedule.objects.get(id=int(schedule_id))
            timeslot = TimeSlot.objects.get(id=int(timeslot_id))
            
            enrollment_date = datetime.now().date()
            if enrollment_date_str:
                enrollment_date = datetime.strptime(enrollment_date_str, '%Y-%m-%d').date()
            
            subsidiary = None
            if subsidiary_id:
                subsidiary = Subsidiary.objects.get(id=int(subsidiary_id))
            
            # Calcular precio, adelanto y faltante
            final_price = Decimal(price) if price else schedule.price
            final_advance = Decimal(advance) if advance else Decimal('0')
            final_remaining = Decimal(remaining) if remaining else max(Decimal('0'), final_price - final_advance)
            
            enrollment = Enrollment.objects.create(
                student=student,
                cycle=cycle,
                schedule=schedule,
                time_slot=timeslot,
                enrollment_date=enrollment_date,
                price=final_price,
                advance=final_advance,
                remaining=final_remaining,
                payment_method=payment_method,
                subsidiary=subsidiary,
                user=request.user if request.user.is_authenticated else None,
                observations=observations,
                status='A',
            )
            
            # Generar PDF del recibo
            pdf_generated = False
            try:
                from .views_PDF import generate_enrollment_receipt_pdf
                pdf_content = generate_enrollment_receipt_pdf(enrollment.id)
                if pdf_content:
                    pdf_generated = True
            except Exception as e:
                print(f"Error generando PDF: {str(e)}")
                # No fallar la creación si el PDF falla
            
            from django.urls import reverse
            pdf_url = reverse('apps.students:download_enrollment_receipt_pdf', args=[enrollment.id])
            
            return JsonResponse({
                'success': True,
                'message': 'Inscripción creada exitosamente',
                'enrollment_id': enrollment.id,
                'pdf_url': pdf_url,
                'pdf_generated': pdf_generated
            })
            
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Deportista no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


def modal_enrollment_update(request):
    """Modal para actualizar inscripción"""
    pk = request.GET.get('pk', '')
    enrollment_obj = None
    cycles = Cycle.objects.filter(is_active=True).prefetch_related('schedules__time_slots')
    subsidiaries = Subsidiary.objects.all()
    
    if pk:
        try:
            enrollment_obj = Enrollment.objects.select_related(
                'student', 'cycle', 'schedule', 'time_slot', 'subsidiary'
            ).get(id=int(pk))
        except Enrollment.DoesNotExist:
            pass

    t = loader.get_template('enrollment/enrollment_update.html')
    return JsonResponse({'form': t.render({
        'enrollment_obj': enrollment_obj,
        'cycles': cycles,
        'subsidiaries': subsidiaries,
    }, request)})


@csrf_exempt
def update_enrollment(request):
    """Actualizar inscripción"""
    if request.method == 'POST':
        try:
            enrollment_id = request.POST.get('enrollment_id', '')
            if not enrollment_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            enrollment = Enrollment.objects.get(id=int(enrollment_id))
            
            cycle_id = request.POST.get('cycle_id', '')
            schedule_id = request.POST.get('schedule_id', '')
            timeslot_id = request.POST.get('timeslot_id', '')
            
            if cycle_id:
                enrollment.cycle = Cycle.objects.get(id=int(cycle_id))
            if schedule_id:
                enrollment.schedule = TrainingSchedule.objects.get(id=int(schedule_id))
            if timeslot_id:
                enrollment.time_slot = TimeSlot.objects.get(id=int(timeslot_id))
            
            enrollment_date_str = request.POST.get('enrollment_date', '')
            if enrollment_date_str:
                enrollment.enrollment_date = datetime.strptime(enrollment_date_str, '%Y-%m-%d').date()
            
            # Actualizar precio, adelanto y faltante
            price = Decimal(request.POST.get('price', enrollment.price))
            advance = Decimal(request.POST.get('advance', enrollment.advance))
            remaining = Decimal(request.POST.get('remaining', enrollment.remaining))
            
            enrollment.price = price
            enrollment.advance = advance
            enrollment.remaining = remaining
            enrollment.payment_method = request.POST.get('payment_method', enrollment.payment_method)
            enrollment.status = request.POST.get('status', enrollment.status)
            enrollment.observations = request.POST.get('observations', '')
            
            subsidiary_id = request.POST.get('subsidiary_id', '')
            if subsidiary_id:
                enrollment.subsidiary = Subsidiary.objects.get(id=int(subsidiary_id))
            
            enrollment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Inscripción actualizada exitosamente'
            })
            
        except Enrollment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Inscripción no encontrada'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# APIs para carga dinámica
# =============================================================================

def get_schedules_by_cycle(request):
    """Obtener schedules por ciclo"""
    cycle_id = request.GET.get('cycle_id', '')
    if cycle_id:
        schedules = TrainingSchedule.objects.filter(
            cycle_id=int(cycle_id), is_active=True
        ).values('id', 'name', 'price')
        return JsonResponse({'schedules': list(schedules)})
    return JsonResponse({'schedules': []})


def get_timeslots_by_schedule(request):
    """Obtener time slots por schedule"""
    schedule_id = request.GET.get('schedule_id', '')
    if schedule_id:
        timeslots = TimeSlot.objects.filter(
            schedule_id=int(schedule_id), is_active=True
        ).values('id', 'start_time', 'end_time', 'age_description')
        
        result = []
        for ts in timeslots:
            result.append({
                'id': ts['id'],
                'display': f"{ts['start_time'].strftime('%H:%M')} - {ts['end_time'].strftime('%H:%M')} ({ts['age_description'] or 'Todas las edades'})"
            })
        return JsonResponse({'timeslots': result})
    return JsonResponse({'timeslots': []})


def search_students(request):
    """Buscar estudiantes para autocompletado"""
    from django.db.models import Q
    query = request.GET.get('q', '')
    if len(query) >= 2:
        students = Student.objects.filter(
            Q(full_name__icontains=query) |
            Q(document_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(surname__icontains=query),
            is_active=True
        )[:10]
        
        results = [{
            'id': s.id,
            'text': f"{s.full_name} - {s.document_number}",
            'full_name': s.full_name,
            'document_number': s.document_number,
        } for s in students]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


def modal_complete_payment(request):
    """Modal para completar pago de inscripción"""
    pk = request.GET.get('pk', '')
    enrollment_obj = None
    
    if pk:
        try:
            enrollment_obj = Enrollment.objects.select_related(
                'student', 'cycle', 'schedule', 'time_slot', 'subsidiary'
            ).get(id=int(pk))
        except Enrollment.DoesNotExist:
            pass
    
    if not enrollment_obj:
        return JsonResponse({
            'success': False,
            'message': 'Inscripción no encontrada'
        }, status=HTTPStatus.NOT_FOUND)
    
    t = loader.get_template('enrollment/enrollment_complete_payment.html')
    return JsonResponse({'form': t.render({'enrollment_obj': enrollment_obj}, request)})


@csrf_exempt
def complete_payment(request):
    """Completar pago de inscripción"""
    if request.method == 'POST':
        try:
            enrollment_id = request.POST.get('enrollment_id', '')
            payment_amount = request.POST.get('payment_amount', '0')
            payment_method = request.POST.get('payment_method', 'E')
            payment_completed_date_str = request.POST.get('payment_completed_date', '')
            observations = request.POST.get('observations', '')
            
            if not enrollment_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de inscripción es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            enrollment = Enrollment.objects.get(id=int(enrollment_id))
            
            payment_amount_decimal = Decimal(payment_amount) if payment_amount else Decimal('0')
            
            if payment_amount_decimal <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'El monto a pagar debe ser mayor a 0'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if payment_amount_decimal > enrollment.remaining:
                return JsonResponse({
                    'success': False,
                    'message': 'El monto no puede ser mayor al faltante'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Actualizar adelanto y faltante
            enrollment.advance += payment_amount_decimal
            enrollment.remaining = max(Decimal('0'), enrollment.remaining - payment_amount_decimal)
            enrollment.payment_method = payment_method
            
            # Si el faltante es 0, marcar como activo
            if enrollment.remaining == 0:
                enrollment.status = 'A'
            
            # Guardar fecha de pago completado
            payment_completed_date = datetime.now().date()
            if payment_completed_date_str:
                payment_completed_date = datetime.strptime(payment_completed_date_str, '%Y-%m-%d').date()
            
            # Agregar observaciones con fecha de pago
            payment_date_text = payment_completed_date.strftime('%d/%m/%Y')
            payment_note = f"[{payment_date_text}] Pago completado: S/ {payment_amount_decimal:.2f}"
            if observations:
                payment_note += f" - {observations}"
            
            if enrollment.observations:
                enrollment.observations += f"\n{payment_note}"
            else:
                enrollment.observations = payment_note
            
            enrollment.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Pago de S/ {payment_amount_decimal:.2f} registrado exitosamente'
            })
            
        except Enrollment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Inscripción no encontrada'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Método no permitido'}, status=HTTPStatus.BAD_REQUEST)
