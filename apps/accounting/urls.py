from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *
from .views_excel import (
    export_sales_report_excel, 
    export_subscriptions_report_excel,
    export_enrollments_report_excel,
    export_students_report_excel,
    export_pending_payments_report_excel
)
from .views_reports import (
    reports_list,
    get_enrollments_report,
    get_students_report,
    get_pending_payments_report
)
from .views_pdf import export_sales_report_pdf

urlpatterns = [
    # URLs para gestión de cuentas/cajas
    path('cash/', login_required(cash_list), name='cash_list'),
    path('cash/create/', login_required(cash_create), name='cash_create'),
    path('cash/save/', login_required(cash_save), name='cash_save'),
    path('cash/get/', login_required(cash_get), name='cash_get'),
    path('cash/<int:cash_id>/edit/', login_required(cash_edit), name='cash_edit'),
    path('cash/update/', login_required(cash_update), name='cash_update'),
    
    # URLs para gestión de gastos (cashflow)
    path('cashflow/', login_required(cashflow_list), name='cashflow_list'),
    path('cashflow/create/', login_required(cashflow_create), name='cashflow_create'),
    path('cashflow/save/', login_required(cashflow_save), name='cashflow_save'),
    path('cashflow/get/', login_required(cashflow_get), name='cashflow_get'),
    path('cashflow/<int:cashflow_id>/edit/', login_required(cashflow_edit), name='cashflow_edit'),
    path('cashflow/update/', login_required(cashflow_update), name='cashflow_update'),
    path('cashflow/delete/', login_required(cashflow_delete), name='cashflow_delete'),
    
    # URLs auxiliares
    path('get-cash-accounts/', login_required(get_cash_accounts_by_subsidiary), name='get_cash_accounts_by_subsidiary'),
    
    # URLs para reportes gráficos
    path('monthly-report/', login_required(monthly_report), name='monthly_report'),
    path('export-subscriptions-report-excel/', login_required(export_subscriptions_report_excel), name='export_subscriptions_report_excel'),
    
    # URLs para reportes de texto/tablas
    path('reports-list/', login_required(reports_list), name='reports_list'),
    path('get-enrollments-report/', login_required(get_enrollments_report), name='get_enrollments_report'),
    path('get-students-report/', login_required(get_students_report), name='get_students_report'),
    path('get-pending-payments-report/', login_required(get_pending_payments_report), name='get_pending_payments_report'),
    
    # URLs para exportar reportes a Excel
    path('export-enrollments-report-excel/', login_required(export_enrollments_report_excel), name='export_enrollments_report_excel'),
    path('export-students-report-excel/', login_required(export_students_report_excel), name='export_students_report_excel'),
    path('export-pending-payments-report-excel/', login_required(export_pending_payments_report_excel), name='export_pending_payments_report_excel'),
]
