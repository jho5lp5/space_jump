from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *
from .views_PDF import download_student_enrollment_pdf, download_enrollment_receipt_pdf
from . import views_cycles

urlpatterns = [
    # =============================================================================
    # URLs PARA GESTIÓN DE ALUMNOS (STUDENTS)
    # =============================================================================
    path('students/', login_required(get_student_list), name='get_student_list'),
    path('students/get-api/', login_required(get_api_student), name='get_api_student'),
    path('modal_student_create/', login_required(modal_student_create), name='modal_student_create'),
    path('students/save/', login_required(save_student), name='save_student'),
    path('students/update-modal/', login_required(modal_student_update), name='modal_student_update'),
    path('students/update/', login_required(update_student), name='update_student'),
    path('students/search-autocomplete/', login_required(search_students_autocomplete), name='search_students_autocomplete'),
    path('students/download-pdf/<int:student_id>/', login_required(download_student_enrollment_pdf), name='download_student_enrollment_pdf'),
    path('students/row-html/<int:student_id>/', login_required(student_row_html), name='student_row_html'),
    path('students/search/', login_required(views_cycles.search_students), name='search_students'),

    # =============================================================================
    # URLs PARA GESTIÓN DE CICLOS (Nueva estructura)
    # =============================================================================
    path('cycles/', login_required(views_cycles.get_cycle_list), name='get_cycle_list'),
    path('cycles/create-modal/', login_required(views_cycles.modal_cycle_create), name='modal_cycle_create'),
    path('cycles/save/', login_required(views_cycles.save_cycle), name='save_cycle'),
    path('cycles/update-modal/', login_required(views_cycles.modal_cycle_update), name='modal_cycle_update'),
    path('cycles/update/', login_required(views_cycles.update_cycle), name='update_cycle'),
    
    # =============================================================================
    # URLs PARA GESTIÓN DE SCHEDULES (Horarios de Entrenamiento)
    # =============================================================================
    path('schedules/create-modal/', login_required(views_cycles.modal_schedule_create), name='modal_schedule_create'),
    path('schedules/save/', login_required(views_cycles.save_schedule), name='save_schedule'),
    path('schedules/update-modal/', login_required(views_cycles.modal_schedule_update), name='modal_schedule_update'),
    path('schedules/update/', login_required(views_cycles.update_schedule), name='update_schedule'),
    path('schedules/by-cycle/', login_required(views_cycles.get_schedules_by_cycle), name='get_schedules_by_cycle'),
    
    # =============================================================================
    # URLs PARA GESTIÓN DE TIME SLOTS (Turnos)
    # =============================================================================
    path('timeslots/create-modal/', login_required(views_cycles.modal_timeslot_create), name='modal_timeslot_create'),
    path('timeslots/save/', login_required(views_cycles.save_timeslot), name='save_timeslot'),
    path('timeslots/update-modal/', login_required(views_cycles.modal_timeslot_update), name='modal_timeslot_update'),
    path('timeslots/update/', login_required(views_cycles.update_timeslot), name='update_timeslot'),
    path('timeslots/by-schedule/', login_required(views_cycles.get_timeslots_by_schedule), name='get_timeslots_by_schedule'),
    
    # =============================================================================
    # URLs PARA GESTIÓN DE INSCRIPCIONES (Enrollment)
    # =============================================================================
    path('enrollments/', login_required(views_cycles.get_enrollment_list), name='get_enrollment_list'),
    path('enrollments/create-modal/', login_required(views_cycles.modal_enrollment_create), name='modal_enrollment_create'),
    path('enrollments/save/', login_required(views_cycles.save_enrollment), name='save_enrollment'),
    path('enrollments/update-modal/', login_required(views_cycles.modal_enrollment_update), name='modal_enrollment_update'),
    path('enrollments/update/', login_required(views_cycles.update_enrollment), name='update_enrollment'),
    
    # =============================================================================
    # URLs DEL DASHBOARD
    # =============================================================================
    path('dashboard/stats/', login_required(dashboard_stats), name='dashboard_stats'),
    path('dashboard/recent-subscriptions/', login_required(recent_subscriptions), name='recent_subscriptions'),
    path('dashboard/monthly-chart/', login_required(monthly_subscriptions_chart), name='monthly_subscriptions_chart'),
    path('dashboard/weekly-chart/', login_required(weekly_subscriptions_chart), name='weekly_subscriptions_chart'),

    # URLs PARA GESTIÓN DE CICLOS (Nueva estructura)
    # =============================================================================
    path('cycles/', login_required(views_cycles.get_cycle_list), name='get_cycle_list'),
    path('cycles/create-modal/', login_required(views_cycles.modal_cycle_create), name='modal_cycle_create'),
    path('cycles/save/', login_required(views_cycles.save_cycle), name='save_cycle'),
    path('cycles/update-modal/', login_required(views_cycles.modal_cycle_update), name='modal_cycle_update'),
    path('cycles/update/', login_required(views_cycles.update_cycle), name='update_cycle'),

    # =============================================================================
    # URLs PARA GESTIÓN DE CICLOS (Nueva estructura)
    # =============================================================================
    path('cycles/', login_required(views_cycles.get_cycle_list), name='get_cycle_list'),
    path('cycles/create-modal/', login_required(views_cycles.modal_cycle_create), name='modal_cycle_create'),
    path('cycles/save/', login_required(views_cycles.save_cycle), name='save_cycle'),
    path('cycles/update-modal/', login_required(views_cycles.modal_cycle_update), name='modal_cycle_update'),
    path('cycles/update/', login_required(views_cycles.update_cycle), name='update_cycle'),

    # URLs PARA GESTIÓN DE ALUMNOS (STUDENTS)
    # =============================================================================
    path('students/search/', login_required(views_cycles.search_students), name='search_students'),

    # URLs PARA GESTIÓN DE SCHEDULES (Horarios de Entrenamiento)
    # =============================================================================
    path('schedules/create-modal/', login_required(views_cycles.modal_schedule_create), name='modal_schedule_create'),
    path('schedules/save/', login_required(views_cycles.save_schedule), name='save_schedule'),
    path('schedules/update-modal/', login_required(views_cycles.modal_schedule_update), name='modal_schedule_update'),
    path('schedules/update/', login_required(views_cycles.update_schedule), name='update_schedule'),
    path('schedules/by-cycle/', login_required(views_cycles.get_schedules_by_cycle), name='get_schedules_by_cycle'),

    # =============================================================================
    # URLs PARA GESTIÓN DE TIME SLOTS (Turnos)
    # =============================================================================
    path('timeslots/create-modal/', login_required(views_cycles.modal_timeslot_create), name='modal_timeslot_create'),
    path('timeslots/save/', login_required(views_cycles.save_timeslot), name='save_timeslot'),
    path('timeslots/update-modal/', login_required(views_cycles.modal_timeslot_update), name='modal_timeslot_update'),
    path('timeslots/update/', login_required(views_cycles.update_timeslot), name='update_timeslot'),
    path('timeslots/by-schedule/', login_required(views_cycles.get_timeslots_by_schedule), name='get_timeslots_by_schedule'),


    # =============================================================================
    # URLs PARA GESTIÓN DE INSCRIPCIONES (Enrollment)
    # =============================================================================
    path('enrollments/', login_required(views_cycles.get_enrollment_list), name='get_enrollment_list'),
    path('enrollments/create-modal/', login_required(views_cycles.modal_enrollment_create), name='modal_enrollment_create'),
    path('enrollments/save/', login_required(views_cycles.save_enrollment), name='save_enrollment'),
    path('enrollments/update-modal/', login_required(views_cycles.modal_enrollment_update), name='modal_enrollment_update'),
    path('enrollments/update/', login_required(views_cycles.update_enrollment), name='update_enrollment'),
    path('enrollments/complete-payment-modal/', login_required(views_cycles.modal_complete_payment), name='modal_complete_payment'),
    path('enrollments/complete-payment/', login_required(views_cycles.complete_payment), name='complete_payment'),
    path('enrollments/receipt-pdf/<int:enrollment_id>/', login_required(download_enrollment_receipt_pdf), name='download_enrollment_receipt_pdf'),
]
