"""
Funciones para gestión de estudiantes
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
    def relativedelta(date1, date2):
        return type('obj', (object,), {'years': (date1 - date2).days // 365})()

from apps.students.models import Student, Cycle, Enrollment
from apps.hrm.models import Subsidiary
from django.db.models import Q, Count

# Create your views here.


def modal_student_create(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        subsidiaries = Subsidiary.objects.all().order_by('name')

        t = loader.get_template('students/student_create.html')
        c = {
            'date_now': date_now,
            'subsidiaries': subsidiaries,
        }
        return JsonResponse({
            'form': t.render(c, request),
        })


def get_student_list(request):
    if request.method == 'GET':
        student_set = Student.objects.filter(is_active=True).order_by('-creation_date')

        # Estadísticas por sede
        subsidiary_stats = Student.objects.values('subsidiary__name').annotate(
            quantity=Count('id')
        ).order_by('-quantity')

        return render(request, 'students/student_list.html', {
            'student_set': student_set,
            'subsidiary_stats': subsidiary_stats,
        })


def get_api_student(request):
    """Buscar estudiante por documento"""
    if request.method == 'GET':
        document_number = request.GET.get('nro_document')
        type_document = str(request.GET.get('type'))
        
        student_set_search = Student.objects.filter(document=type_document, document_number=document_number)
        if student_set_search.exists():
            student_obj = student_set_search.last()
            return JsonResponse({
                'pk': student_obj.id,
                'names': student_obj.full_name,
                'firstName': student_obj.first_name or '',
                'secondName': student_obj.second_name or '',
                'surname': student_obj.surname or '',
                'secondSurname': student_obj.second_surname or '',
                'phone': student_obj.phone or '',
                'address': student_obj.address or '',
                'message': 'Deportista encontrado en BD'
            }, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                'error': 'Deportista no encontrado. Registre manualmente.'
            }, status=HTTPStatus.NOT_FOUND)

    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def save_student(request):
    """Guardar nuevo estudiante"""
    if request.method == 'POST':
        try:
            # Datos personales del deportista
            document = request.POST.get('document', '01')
            document_number = request.POST.get('document_number', '')
            first_name = request.POST.get('first_name', '')
            second_name = request.POST.get('second_name', '')
            surname = request.POST.get('surname', '')
            second_surname = request.POST.get('second_surname', '')
            birth_place = request.POST.get('birth_place', '')
            birth_date_str = request.POST.get('birth_date', '')
            address = request.POST.get('address', '')
            phone = request.POST.get('phone', '')

            # Datos del padre/madre/apoderado
            parent_first_name = request.POST.get('parent_first_name', '')
            parent_surname = request.POST.get('parent_surname', '')
            parent_document = request.POST.get('parent_document', '01')
            parent_document_number = request.POST.get('parent_document_number', '')
            parent_phone = request.POST.get('parent_phone', '')

            # Historia clínica
            diseases = request.POST.get('diseases', '')
            medication_allergies = request.POST.get('medication_allergies', '')
            student_insurance = request.POST.get('student_insurance', '')
            sports_injuries = request.POST.get('sports_injuries', '')
            other_medical_info = request.POST.get('other_medical_info', '')

            # Información adicional
            subsidiary_id = request.POST.get('subsidiary', '')
            observations = request.POST.get('observations', '')

            # Validaciones básicas
            if not document_number or not first_name or not surname:
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos DNI, Nombres y Apellidos son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)

            # Procesar fechas
            birth_date = None
            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except:
                    pass

            # Calcular edad actual
            current_age = None
            if birth_date:
                current_age = relativedelta(datetime.now().date(), birth_date).years

            # Obtener sucursal
            subsidiary = None
            if subsidiary_id:
                try:
                    subsidiary = Subsidiary.objects.get(id=int(subsidiary_id))
                except:
                    pass

            # Crear estudiante
            student = Student(
                document=document,
                document_number=document_number,
                first_name=first_name.upper(),
                second_name=second_name.upper() if second_name else '',
                surname=surname.upper(),
                second_surname=second_surname.upper() if second_surname else '',
                birth_place=birth_place.upper() if birth_place else '',
                birth_date=birth_date,
                address=address.upper() if address else '',
                phone=phone,
                parent_first_name=parent_first_name.upper() if parent_first_name else '',
                parent_surname=parent_surname.upper() if parent_surname else '',
                parent_document=parent_document,
                parent_document_number=parent_document_number,
                parent_phone=parent_phone,
                diseases=diseases,
                medication_allergies=medication_allergies,
                student_insurance=student_insurance,
                sports_injuries=sports_injuries,
                other_medical_info=other_medical_info,
                current_age=current_age,
                subsidiary=subsidiary,
                observations=observations,
            )

            # Manejar foto si se subió
            if 'photo' in request.FILES:
                student.photo = request.FILES['photo']

            student.save()

            # Generar PDF de inscripción
            try:
                from .views_PDF import generate_student_enrollment_pdf
                pdf_content = generate_student_enrollment_pdf(student.id)
                if pdf_content:
                    import base64
                    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                    pdf_filename = f"FICHA_INSCRIPCION_{student.document_number}_{student.id}.pdf"

                    return JsonResponse({
                        'success': True,
                        'message': 'Deportista registrado exitosamente',
                        'student_id': student.id,
                        'pdf_content': pdf_base64,
                        'pdf_filename': pdf_filename
                    }, status=HTTPStatus.OK)
            except Exception as pdf_error:
                # Si hay error al generar PDF, continuar sin él
                print(f"Error generando PDF: {str(pdf_error)}")

            return JsonResponse({
                'success': True,
                'message': 'Deportista registrado exitosamente',
                'student_id': student.id
            }, status=HTTPStatus.OK)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar el deportista: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def modal_student_update(request):
    """Modal para actualizar estudiante"""
    if request.method == 'GET':
        pk = request.GET.get('pk', '')
        student_obj = None
        if pk:
            try:
                student_obj = Student.objects.get(id=int(pk))
            except Student.DoesNotExist:
                pass

        subsidiaries = Subsidiary.objects.all().order_by('name')

        t = loader.get_template('students/student_update.html')
        c = {
            'student_obj': student_obj,
            'subsidiaries': subsidiaries,
        }
        return JsonResponse({
            'form': t.render(c, request),
        })


@csrf_exempt
def update_student(request):
    """Actualizar estudiante existente"""
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id', '')
            if not student_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de deportista es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)

            student = Student.objects.get(id=int(student_id))

            # Actualizar campos (similar a save_student)
            student.document = request.POST.get('document', student.document)
            student.document_number = request.POST.get('document_number', student.document_number)
            student.first_name = request.POST.get('first_name', student.first_name).upper()
            student.second_name = request.POST.get('second_name', '').upper()
            student.surname = request.POST.get('surname', student.surname).upper()
            student.second_surname = request.POST.get('second_surname', '').upper()
            student.birth_place = request.POST.get('birth_place', '').upper()
            student.address = request.POST.get('address', '').upper()
            student.phone = request.POST.get('phone', '')
            student.parent_first_name = request.POST.get('parent_first_name', '').upper()
            student.parent_surname = request.POST.get('parent_surname', '').upper()
            student.parent_document = request.POST.get('parent_document', '01')
            student.parent_document_number = request.POST.get('parent_document_number', '')
            student.parent_phone = request.POST.get('parent_phone', '')
            student.diseases = request.POST.get('diseases', '')
            student.medication_allergies = request.POST.get('medication_allergies', '')
            student.student_insurance = request.POST.get('student_insurance', '')
            student.sports_injuries = request.POST.get('sports_injuries', '')
            student.other_medical_info = request.POST.get('other_medical_info', '')
            student.observations = request.POST.get('observations', '')

            # Procesar fechas
            birth_date_str = request.POST.get('birth_date', '')
            if birth_date_str:
                try:
                    student.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    student.current_age = relativedelta(datetime.now().date(), student.birth_date).years
                except:
                    pass

            # Sucursal
            subsidiary_id = request.POST.get('subsidiary', '')
            if subsidiary_id:
                try:
                    student.subsidiary = Subsidiary.objects.get(id=int(subsidiary_id))
                except:
                    pass
                if subsidiary_id == '':
                    student.subsidiary = None

            # Foto
            if 'photo' in request.FILES:
                student.photo = request.FILES['photo']

            student.save()

            return JsonResponse({
                'success': True,
                'message': 'Deportista actualizado exitosamente'
            }, status=HTTPStatus.OK)

        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Deportista no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar el deportista: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def search_students_autocomplete(request):
    """Búsqueda de estudiantes para autocompletado"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})

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


# =============================================================================
# FUNCIONES DEL DASHBOARD
# =============================================================================


def dashboard_stats(request):
    """Estadísticas del dashboard"""
    if request.method == 'GET':
        from django.db.models import Count, Sum

        total_students = Student.objects.filter(is_active=True).count()
        total_enrollments = Enrollment.objects.filter(status='A').count()
        total_cycles = Cycle.objects.filter(is_active=True).count()

        # Ingresos del mes actual
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_income = Enrollment.objects.filter(
            creation_date__year=current_year,
            creation_date__month=current_month
        ).aggregate(total=Sum('price'))['total'] or 0

        return JsonResponse({
            'total_students': total_students,
            'total_subscriptions': total_enrollments,
            'total_plans': total_cycles,
            'monthly_income': float(monthly_income),
        })


def recent_subscriptions(request):
    """Inscripciones recientes"""
    if request.method == 'GET':
        enrollments = Enrollment.objects.select_related('student', 'cycle').order_by('-creation_date')[:10]

        data = [{
            'id': e.id,
            'student_name': e.student.full_name,
            'plan_name': e.cycle.name if e.cycle else 'Sin ciclo',
            'price': str(e.price),
            'status': e.get_status_display(),
            'creation_date': e.creation_date.strftime('%d/%m/%Y') if e.creation_date else '',
        } for e in enrollments]

        return JsonResponse({'subscriptions': data})


def monthly_subscriptions_chart(request):
    """Gráfico mensual de inscripciones"""
    if request.method == 'GET':
        from django.db.models import Count
        from django.db.models.functions import TruncMonth

        enrollments = Enrollment.objects.annotate(
            month=TruncMonth('creation_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        data = {
            'labels': [e['month'].strftime('%b %Y') for e in enrollments if e['month']],
            'data': [e['count'] for e in enrollments if e['month']],
        }

        return JsonResponse(data)


def weekly_subscriptions_chart(request):
    """Gráfico semanal de inscripciones"""
    if request.method == 'GET':
        from django.db.models import Count
        from django.db.models.functions import TruncWeek

        enrollments = Enrollment.objects.annotate(
            week=TruncWeek('creation_date')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')[:8]

        data = {
            'labels': [e['week'].strftime('%d/%m') for e in enrollments if e['week']],
            'data': [e['count'] for e in enrollments if e['week']],
        }

        return JsonResponse(data)