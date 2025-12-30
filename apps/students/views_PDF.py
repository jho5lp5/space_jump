from django.db.models import Prefetch, Q
from reportlab.lib.pagesizes import letter, landscape, A4, A5, C7
import io
import pdfkit
import decimal
import reportlab
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.lib.colors import black, blue, red, Color
from reportlab.lib.pagesizes import landscape, A5, portrait, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer, Image, Flowable, HRFlowable, PageBreak, KeepTogether
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.rl_settings import defaultPageSize
from space import settings
import io
from django.conf import settings
import datetime
from datetime import datetime
import requests

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, leading=8, fontName='Square', fontSize=14))
styles.add(ParagraphStyle(name='Center-Blue', alignment=TA_CENTER, leading=8, fontName='Square-Bold', fontSize=14,
                          textColor=colors.cornflowerblue))
styles.add(ParagraphStyle(name='Center_White', alignment=TA_CENTER, leading=8, fontName='Square', fontSize=14,
                          textColor=colors.white))
styles.add(ParagraphStyle(name='Left_Square', alignment=TA_LEFT, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Left_Newgot', alignment=TA_LEFT, leading=12, fontName='Newgot', fontSize=10))
styles.add(ParagraphStyle(name='Center_Newgot', alignment=TA_CENTER, leading=12, fontName='Newgot', fontSize=10))
styles.add(
    ParagraphStyle(name='Justify_Newgot_title', alignment=TA_JUSTIFY, leading=14, fontName='Newgot', fontSize=14))
styles.add(
    ParagraphStyle(name='Justify_Newgot_text', alignment=TA_JUSTIFY, leading=10, fontName='Newgot', fontSize=12))
styles.add(
    ParagraphStyle(name='Justify_Newgot_text_red', alignment=TA_CENTER, leading=14, fontName='Newgot', fontSize=14,
                   textColor=colors.darkred))
styles.add(ParagraphStyle(name='Center_Newgot_title', alignment=TA_CENTER, leading=15, fontName='Newgot', fontSize=15))
styles.add(ParagraphStyle(name='Center_Newgot_title_blue', alignment=TA_CENTER, leading=15, fontName='Newgot',
                          fontSize=15, textColor=colors.dodgerblue))
styles.add(
    ParagraphStyle(name='Center_Newgot_title_f12', alignment=TA_CENTER, leading=15, fontName='Newgot', fontSize=12))
styles.add(
    ParagraphStyle(name='Center_Newgot_sub_title', alignment=TA_CENTER, leading=10, fontName='Newgot', fontSize=10,
                   textColor=colors.lightslategrey))
styles.add(
    ParagraphStyle(name='Center_Newgot_sub_title_2', alignment=TA_CENTER, leading=10, fontName='Newgot', fontSize=8))
styles.add(
    ParagraphStyle(name='Center_Newgot_sub_title_3', alignment=TA_CENTER, leading=10, fontName='Newgot', fontSize=10))
styles.add(ParagraphStyle(name='Justify_Square', alignment=TA_JUSTIFY, leading=12, fontName='Square', fontSize=11))
styles.add(ParagraphStyle(name='Justify_Square_Blue', alignment=TA_JUSTIFY, leading=10, fontName='Square', fontSize=10,
                          textColor=colors.dodgerblue))
styles.add(
    ParagraphStyle(name='Justify_Square_bold', alignment=TA_JUSTIFY, leading=10, fontName='Square-Bold', fontSize=10))

reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
pdfmetrics.registerFont(TTFont('Square', 'square-721-condensed-bt.ttf'))
pdfmetrics.registerFont(TTFont('Square-Bold', 'sqr721bc.ttf'))
pdfmetrics.registerFont(TTFont('Newgot', 'newgotbc.ttf'))

logo = "static/assets/img/log_medrano_no_bg.png"

I = Image(logo)
I.drawHeight = 3.10 * inch / 2.9
I.drawWidth = 6.1 * inch / 2.9

_a4 = (8.3 * inch, 11.7 * inch)
ml = 0.25 * inch
mr = 0.25 * inch
ms = 0.25 * inch
mi = 0.25 * inch


def generate_student_enrollment_pdf(student_id):
    """
    Genera un PDF profesional de la ficha de inscripción del deportista
    Formato A4 con diseño moderno y profesional
    """
    try:
        from .models import Student, Enrollment
        from ..hrm.models import Subsidiary
        import os

        # Obtener el estudiante
        student = Student.objects.select_related('subsidiary').get(id=student_id)
        
        # Obtener la inscripción más reciente del estudiante
        enrollment = Enrollment.objects.filter(
            student=student
        ).select_related('schedule', 'time_slot').order_by('-enrollment_date', '-creation_date').first()
        
        # Obtener información del horario
        schedule_text = ""
        if enrollment and enrollment.schedule:
            schedule_name = enrollment.schedule.name.upper()
            if enrollment.time_slot:
                time_slot_text = f"{enrollment.time_slot.start_time.strftime('%H:%M')} - {enrollment.time_slot.end_time.strftime('%H:%M')}"
                schedule_text = f"{schedule_name} ({time_slot_text})"
            else:
                schedule_text = schedule_name
        
        # Obtener fecha de inscripción
        enrollment_date_text = ""
        if enrollment and enrollment.enrollment_date:
            enrollment_date_text = enrollment.enrollment_date.strftime('%d/%m/%Y')

        # Crear el buffer para el PDF
        buffer = io.BytesIO()

        # Configurar el documento A4 con márgenes profesionales
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title='FICHA DE INSCRIPCIÓN - SPACE JUMP'
        )

        # Lista de elementos del PDF
        elements = []

        # Estilos personalizados
        styles = getSampleStyleSheet()

        # Estilo para título principal
        title_style = ParagraphStyle(
            name='TitleStyle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=18
        )

        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            name='SubtitleStyle',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=14
        )

        # Estilo para secciones
        section_style = ParagraphStyle(
            name='SectionStyle',
            parent=styles['Heading3'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=3,
            spaceBefore=5,
            fontName='Helvetica-Bold',
            leading=13
        )

        # Estilo para etiquetas
        label_style = ParagraphStyle(
            name='LabelStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=10
        )

        # Estilo para valores
        value_style = ParagraphStyle(
            name='ValueStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            leading=10
        )
        
        # Estilo para horario (antes del logo)
        horario_style = ParagraphStyle(
            name='HorarioStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=11,
            alignment=TA_LEFT
        )
        
        # Estilo para fecha de inscripción
        fecha_inscripcion_style = ParagraphStyle(
            name='FechaInscripcionStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=11,
            alignment=TA_LEFT
        )

        # ========== HORARIO (ANTES DEL LOGO) ==========
        elements.append(Paragraph(f'HORARIO: {schedule_text}', horario_style))
        elements.append(Spacer(1, 0.2 * cm))

        # ========== ENCABEZADO CON LOGO ==========
        # Buscar el logo
        logo_path = None
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'space_jump_logo_no_bg.png'),
            os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'space_black_an_white.png'),
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                logo_path = path
                break
        
        # Crear tabla de encabezado con logo a la izquierda
        header_data = []
        if logo_path:
            try:
                logo_img = Image(logo_path)
                logo_img.drawHeight = 3.0 * cm
                logo_img.drawWidth = 3.0 * cm
                header_data.append([
                    logo_img,
                    [
                        Paragraph('ESCUELA DE ENTRENAMIENTO FÍSICO - FUNCIONAL', title_style),
                        Paragraph('"SPACE JUMP"', title_style),
                        Paragraph('ACADEMIA FORMATIVA DE BASQUETBALL', subtitle_style),
                    ]
                ])
            except:
                header_data.append([
                    Paragraph('', value_style),
                    [
                        Paragraph('ESCUELA DE ENTRENAMIENTO FÍSICO - FUNCIONAL "SPACE JUMP"', title_style),
                        Paragraph('ACADEMIA FORMATIVA DE BASQUETBALL', subtitle_style),
                    ]
                ])
        else:
            header_data.append([
                Paragraph('', value_style),
                [
                    Paragraph('ESCUELA DE ENTRENAMIENTO FÍSICO - FUNCIONAL "SPACE JUMP"', title_style),
                    Paragraph('ACADEMIA FORMATIVA DE BASQUETBALL', subtitle_style),
                ]
            ])

        header_table = Table(header_data, colWidths=[3.5 * cm, 14.5 * cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=3))

        # ========== INFORMACIÓN DEL CICLO ==========
        # cycle_data = []
        # enrollment_cycle = student.enrollment_cycle or 'VERANO 2025'
        # enrollment_date = student.enrollment_date.strftime(
        #     '%d/%m/%Y') if student.enrollment_date else datetime.now().strftime('%d/%m/%Y')
        # current_age = f"{student.current_age} años" if student.current_age else "N/A"
        #
        # cycle_data.append([
        #     Paragraph('CICLO:', label_style),
        #     Paragraph(enrollment_cycle, value_style),
        #     Paragraph('FECHA INSCRIPCIÓN:', label_style),
        #     Paragraph(enrollment_date, value_style),
        #     Paragraph('EDAD ACTUAL:', label_style),
        #     Paragraph(current_age, value_style),
        # ])
        #
        # cycle_table = Table(cycle_data, colWidths=[2.5 * cm, 4 * cm, 3 * cm, 3 * cm, 2.5 * cm, 3 * cm])
        # cycle_table.setStyle(TableStyle([
        #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        #     ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f5f5f5')),
        #     ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#f5f5f5')),
        #     ('BACKGROUND', (4, 0), (4, 0), colors.HexColor('#f5f5f5')),
        #     ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdbdbd')),
        #     ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        #     ('LEFTPADDING', (0, 0), (-1, -1), 6),
        #     ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        #     ('TOPPADDING', (0, 0), (-1, -1), 6),
        #     ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # ]))
        # elements.append(cycle_table)
        # elements.append(Spacer(1, 0.5 * cm))

        # ========== TÍTULO FICHA DE INSCRIPCIÓN ==========
        ficha_title_style = ParagraphStyle(
            name='FichaTitleStyle',
            parent=styles['Heading1'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=1,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=15
        )
        elements.append(Paragraph('FICHA DE INSCRIPCIÓN', ficha_title_style))
        
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=3))
        
        # ========== FECHA DE INSCRIPCIÓN (DESPUÉS DE LA LÍNEA) ==========
        elements.append(Paragraph(f'FECHA DE INSCRIPCIÓN: {enrollment_date_text}', fecha_inscripcion_style))
        elements.append(Spacer(1, 0.2 * cm))

        # ========== DATOS PERSONALES DEL DEPORTISTA ==========
        elements.append(Paragraph('DATOS PERSONALES DEL DEPORTISTA', section_style))

        # Preparar datos personales
        student_photo_path = None
        if student.photo and student.photo.url:
            try:
                photo_path = os.path.join(settings.MEDIA_ROOT, student.photo.name)
                if os.path.exists(photo_path):
                    student_photo_path = photo_path
            except:
                pass

        # Si no hay foto, usar una imagen por defecto
        if not student_photo_path:
            default_photo = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'dist/img/employee0.jpg')
            if os.path.exists(default_photo):
                student_photo_path = default_photo

        # Crear tabla de datos personales con foto mejorada
        personal_data = []

        # Primera fila: Tipo Doc, Número Doc y Foto
        doc_type = student.get_document_display() if hasattr(student, 'get_document_display') else 'DNI'

        # Preparar celda de foto con borde
        photo_cell = Paragraph('FOTO', ParagraphStyle(
            name='PhotoLabel',
            parent=value_style,
            alignment=TA_CENTER,
            fontSize=9
        ))
        if student_photo_path:
            try:
                photo_cell = Image(student_photo_path, width=3.5 * cm, height=4.5 * cm)
            except:
                photo_cell = Paragraph('FOTO', ParagraphStyle(
                    name='PhotoLabel',
                    parent=value_style,
                    alignment=TA_CENTER,
                    fontSize=9
                ))

        personal_data.append([
            [Paragraph('Tipo Doc:', label_style), Paragraph(doc_type, value_style)],
            [Paragraph('N° Documento:', label_style), Paragraph(student.document_number or '-', value_style)],
            photo_cell
        ])

        # Segunda fila: Nombres y Apellidos
        names = student.first_name or ''
        surnames = student.surname or ''
        if student.second_name:
            names += ' ' + student.second_name
        if student.second_surname:
            surnames += ' ' + student.second_surname

        personal_data.append([
            [Paragraph('Nombres:', label_style), Paragraph(names, value_style)],
            [Paragraph('Apellidos:', label_style), Paragraph(surnames, value_style)],
            Paragraph('', value_style)  # Celda vacía para mantener estructura
        ])

        # Tercera fila: Lugar y Fecha de Nacimiento
        birth_place = student.birth_place or '-'
        birth_date = student.birth_date.strftime('%d/%m/%Y') if student.birth_date else '-'
        current_age = f"{student.current_age} años" if student.current_age else '-'
        personal_data.append([
            [Paragraph('Lugar de Nacimiento:', label_style), Paragraph(birth_place, value_style)],
            [Paragraph('Fecha de Nacimiento:', label_style), Paragraph(f"{birth_date} ({current_age})", value_style)],
            Paragraph('', value_style)  # Celda vacía
        ])

        # Cuarta fila: Domicilio
        address = student.address or '-'
        personal_data.append([
            [Paragraph('Domicilio:', label_style), Paragraph(address, value_style)],
            Paragraph('', value_style),
            Paragraph('', value_style)  # Celda vacía
        ])

        # Quinta fila: Teléfono
        phone = student.phone or '-'
        personal_data.append([
            [Paragraph('Teléfono Celular:', label_style), Paragraph(phone, value_style)],
            Paragraph('', value_style),
            Paragraph('', value_style)  # Celda vacía
        ])

        personal_table = Table(personal_data, colWidths=[5.5 * cm, 5.5 * cm, 7 * cm])
        personal_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('VALIGN', (2, 0), (2, 0), 'TOP'),
            ('BACKGROUND', (0, 0), (1, 4), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#ffffff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('SPAN', (2, 0), (2, 4)),  # La foto ocupa 5 filas
        ]))
        elements.append(personal_table)
        elements.append(Spacer(1, 0.1 * cm))

        # ========== DATOS DEL PADRE/MADRE/APODERADO ==========
        elements.append(Paragraph('DATOS PERSONALES DEL PADRE/ MADRE/ APODERADO', section_style))

        parent_data = []
        # Obtener tipo de documento del padre
        parent_doc_type = 'DNI'
        if student.parent_document:
            if student.parent_document == '01':
                parent_doc_type = 'DNI'
            elif student.parent_document == '06':
                parent_doc_type = 'RUC'
            else:
                parent_doc_type = 'DNI'

        parent_data.append([
            [Paragraph('Nombres:', label_style), Paragraph(student.parent_first_name or '-', value_style)],
            [Paragraph('Apellidos:', label_style), Paragraph(student.parent_surname or '-', value_style)],
        ])
        parent_data.append([
            [Paragraph('Tipo Doc:', label_style), Paragraph(parent_doc_type, value_style)],
            [Paragraph('N° Documento:', label_style), Paragraph(student.parent_document_number or '-', value_style)],
        ])
        parent_data.append([
            [Paragraph('Teléfono:', label_style), Paragraph(student.parent_phone or '-', value_style)],
            [Paragraph('', value_style), Paragraph('', value_style)],
        ])

        parent_table = Table(parent_data, colWidths=[9 * cm, 9 * cm])
        parent_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(parent_table)
        elements.append(Spacer(1, 0.1 * cm))

        # ========== HISTORIA CLÍNICA ==========
        elements.append(Paragraph('HISTORIA CLÍNICA DEL DEPORTISTA', section_style))

        clinical_data = []
        clinical_data.append([
            [Paragraph('Enfermedades:', label_style), Paragraph(student.diseases or '-', value_style)],
            [Paragraph('Alergia a Medicamentos:', label_style),
             Paragraph(student.medication_allergies or '-', value_style)],
        ])
        clinical_data.append([
            [Paragraph('Seguro del Estudiante:', label_style),
             Paragraph(student.student_insurance or '-', value_style)],
            [Paragraph('Lesiones Deportivas:', label_style), Paragraph(student.sports_injuries or '-', value_style)],
        ])
        clinical_data.append([
            [Paragraph('Otros:', label_style), Paragraph(student.other_medical_info or '-', value_style)],
            [Paragraph('', value_style), Paragraph('', value_style)],
        ])

        clinical_table = Table(clinical_data, colWidths=[9 * cm, 9 * cm])
        clinical_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(clinical_table)
        elements.append(Spacer(1, 1.0 * cm))
        
        # ========== FIRMA AUTORIZACIÓN DE PARTICIPACIÓN ==========
        # Buscar el sello
        sello_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'sello_space.png')
        sello_img = None
        if os.path.exists(sello_path):
            try:
                sello_img = Image(sello_path)
                sello_img.drawHeight = 2.5 * cm
                sello_img.drawWidth = 3.0 * cm
            except:
                sello_img = None
        
        # Crear tabla con sello a la izquierda y firma a la derecha
        # Crear una tabla anidada para el lado derecho con todos los elementos de firma
        firma_right_data = []
        firma_right_data.append([
            HRFlowable(width=8*cm, thickness=0.5, color=colors.black, spaceBefore=0, spaceAfter=2)
        ])
        firma_right_data.append([
            Paragraph('FIRMA AUTORIZACION DE PARTICIPACION', ParagraphStyle(
                name='FirmaTitle',
                parent=label_style,
                fontSize=9,
                alignment=TA_CENTER,
                spaceAfter=8
            ))
        ])
        firma_right_data.append([
            Paragraph('PADRE/MADRE DE FAMILIA', ParagraphStyle(
                name='FirmaSubtitle',
                parent=value_style,
                fontSize=8,
                alignment=TA_CENTER
            ))
        ])
        
        firma_right_table = Table(firma_right_data, colWidths=[9 * cm])
        firma_right_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        firma_data = []
        # Sello a la izquierda, firma a la derecha
        if sello_img:
            firma_cell = [sello_img, firma_right_table]
        else:
            firma_cell = [Paragraph('', value_style), firma_right_table]
        
        firma_data.append(firma_cell)
        
        firma_table = Table(firma_data, colWidths=[9 * cm, 9 * cm])
        firma_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        elements.append(firma_table)
        elements.append(Spacer(1, 1.5 * cm))
        
        # ========== TEXTO FINAL (PIE DE PÁGINA) ==========
        elements.append(Paragraph(
            'ESCUELA DE ENTRENAMIENTO FISICO - FUNCIONAL | PROF. LUIS CARRAZCO PINTO',
            ParagraphStyle(
                name='FinalText1',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=1
            )
        ))
        elements.append(Paragraph(
            'ACADEMIA DE BASQUET SPACE JUMP',
            ParagraphStyle(
                name='FinalText2',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=0.3 * cm
            )
        ))
        
        # ========== DECLARACIÓN JURADA (COMENTADA - USUARIO NO ESTÁ SEGURO SI LA DESEA USAR) ==========
        # elements.append(PageBreak())
        #
        # # ========== DECLARACIÓN JURADA (FORMULARIO COMPLETO) ==========
        # declaration_title_style = ParagraphStyle(
        #     name='DeclarationTitleStyle',
        #     parent=styles['Heading1'],
        #     fontSize=14,
        #     textColor=colors.black,
        #     spaceAfter=0.8 * cm,
        #     alignment=TA_CENTER,
        #     fontName='Helvetica-Bold',
        #     leading=18
        # )
        # elements.append(Paragraph('DECLARACIÓN JURADA Y AUTORIZACIÓN', declaration_title_style))
        # elements.append(Spacer(1, 0.3 * cm))
        #
        # # Estilo para campos del formulario
        # field_label_style = ParagraphStyle(
        #     name='FieldLabelStyle',
        #     parent=styles['Normal'],
        #     fontSize=9,
        #     textColor=colors.black,
        #     fontName='Helvetica-Bold',
        #     leading=11,
        #     alignment=TA_LEFT
        # )
        #
        # field_value_style = ParagraphStyle(
        #     name='FieldValueStyle',
        #     parent=styles['Normal'],
        #     fontSize=9,
        #     textColor=colors.black,
        #     fontName='Helvetica',
        #     leading=11,
        #     alignment=TA_LEFT
        # )
        #
        # # Obtener datos del padre/madre
        # parent_full_name = f"{student.parent_first_name or ''} {student.parent_surname or ''}".strip()
        # parent_doc_number = student.parent_document_number or ''
        # student_full_name = f"{names} {surnames}".strip()
        # student_doc_number = student.document_number or ''
        # current_date = datetime.now()
        # fecha_texto = f"{current_date.strftime('%d')} de {current_date.strftime('%B')} del {current_date.strftime('%Y')}"
        #
        # # Crear formulario de declaración jurada
        # declaration_form_data = []
        #
        # # Texto introductorio
        # intro_text = Paragraph(
        #     'Yo, el/la que suscribe, declaro bajo juramento que la información proporcionada es verídica y autorizo a la Escuela de Entrenamiento Físico - Funcional "SPACE JUMP" para el uso de los datos del menor con fines administrativos y deportivos.',
        #     ParagraphStyle(
        #         name='IntroText',
        #         parent=styles['Normal'],
        #         fontSize=9,
        #         textColor=colors.black,
        #         fontName='Helvetica',
        #         alignment=TA_JUSTIFY,
        #         leading=12,
        #         spaceAfter=0.6 * cm
        #     )
        # )
        # declaration_form_data.append([intro_text])
        #
        # # Datos del padre/madre/apoderado
        # declaration_form_data.append([
        #     Paragraph('DATOS DEL PADRE/MADRE/APODERADO:', field_label_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>Nombres y Apellidos:</b> {parent_full_name}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>Tipo de Documento:</b> {parent_doc_type}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>N° de Documento:</b> {parent_doc_number}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph('', value_style)  # Espacio
        # ])
        #
        # # Datos del menor
        # declaration_form_data.append([
        #     Paragraph('DATOS DEL MENOR:', field_label_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>Nombres y Apellidos:</b> {student_full_name}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>Tipo de Documento:</b> {doc_type}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph(f'<b>N° de Documento:</b> {student_doc_number}', field_value_style)
        # ])
        # declaration_form_data.append([
        #     Paragraph('', value_style)  # Espacio
        # ])
        #
        # # Firma y fecha
        # declaration_form_data.append([
        #     Paragraph('', value_style)  # Espacio adicional
        # ])
        # declaration_form_data.append([
        #     Paragraph('', value_style),
        #     Paragraph('', value_style)
        # ])
        #
        # # Tabla para firma y fecha
        # firma_declaration_data = []
        # firma_declaration_data.append([
        #     Paragraph('_________________________', ParagraphStyle(
        #         name='FirmaLine',
        #         parent=value_style,
        #         fontSize=9,
        #         alignment=TA_LEFT
        #     )),
        #     Paragraph(f'Arequipa, {fecha_texto}', ParagraphStyle(
        #         name='FechaLine',
        #         parent=value_style,
        #         fontSize=9,
        #         alignment=TA_RIGHT
        #     ))
        # ])
        # firma_declaration_data.append([
        #     Paragraph('Firma del Padre/Madre/Apoderado', field_label_style),
        #     Paragraph('Fecha', field_label_style)
        # ])
        #
        # firma_declaration_table = Table(firma_declaration_data, colWidths=[9 * cm, 9 * cm])
        # firma_declaration_table.setStyle(TableStyle([
        #     ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        #     ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        #     ('TOPPADDING', (0, 0), (0, 0), 30),
        #     ('LEFTPADDING', (0, 0), (-1, -1), 0),
        #     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        # ]))
        #
        # # Crear tabla principal del formulario
        # declaration_table = Table(declaration_form_data, colWidths=[18 * cm])
        # declaration_table.setStyle(TableStyle([
        #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        #     ('LEFTPADDING', (0, 0), (-1, -1), 0.5 * cm),
        #     ('RIGHTPADDING', (0, 0), (-1, -1), 0.5 * cm),
        #     ('TOPPADDING', (0, 0), (-1, -1), 3),
        #     ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        # ]))
        # elements.append(declaration_table)
        # elements.append(Spacer(1, 0.3 * cm))
        # elements.append(firma_declaration_table)
        # elements.append(Spacer(1, 0.5 * cm))

        # Construir el PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    except Exception as e:
        print(f"Error generando PDF de inscripción: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def download_student_enrollment_pdf(request, student_id):
    """
    Vista para descargar el PDF de la ficha de inscripción del deportista
    """
    try:
        from .models import Student
        from django.http import HttpResponse

        # Verificar que el estudiante existe
        student = Student.objects.get(id=student_id)

        # Generar el PDF
        pdf_content = generate_student_enrollment_pdf(student_id)

        if pdf_content:
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            # Nombre del archivo
            filename = f"FICHA_INSCRIPCION_{student.document_number or student.id}_{student.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse("Error generando el PDF", status=500)

    except Student.DoesNotExist:
        return HttpResponse("Deportista no encontrado", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def generate_enrollment_receipt_pdf(enrollment_id):
    """
    Genera un PDF de recibo de inscripción en formato ticket
    """
    try:
        from .models import Enrollment
        import os
        from django.conf import settings

        # Obtener la inscripción
        enrollment = Enrollment.objects.select_related(
            'student', 'cycle', 'schedule', 'time_slot', 'subsidiary'
        ).get(id=enrollment_id)

        # Crear el buffer para el PDF
        buffer = io.BytesIO()

        # Configurar el documento con el ancho especificado para tickets
        _wt = 2.93 * inch - 4 * 0.05 * inch
        pz_thermal = (2.93 * inch, 11.6 * inch)

        ml = 0.01 * inch
        mr = 0.05 * inch
        ms = 0.039 * inch
        mi = 0.039 * inch

        doc = SimpleDocTemplate(
            buffer,
            pagesize=pz_thermal,
            rightMargin=mr,
            leftMargin=ml,
            topMargin=ms,
            bottomMargin=mi,
            title='RECIBO DE INSCRIPCIÓN'
        )

        # Lista de elementos del PDF
        elements = []

        # Estilos para el ticket con espaciado reducido
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Center_10',
            alignment=TA_CENTER,
            leading=11,
            fontName='Helvetica-Bold',
            fontSize=10
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Center_8',
            alignment=TA_CENTER,
            leading=8,
            fontName='Helvetica-Bold',
            fontSize=8
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Center_7',
            alignment=TA_CENTER,
            leading=7,
            fontName='Helvetica-Bold',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Center_6',
            alignment=TA_CENTER,
            leading=7,
            fontName='Helvetica-Bold',
            fontSize=6
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Right_7',
            alignment=TA_RIGHT,
            leading=7,
            fontName='Helvetica-Bold',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Right_6',
            alignment=TA_RIGHT,
            leading=7,
            fontName='Helvetica-Bold',
            fontSize=6
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Center_7',
            alignment=TA_CENTER,
            leading=8,
            fontName='Helvetica',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Center_6',
            alignment=TA_CENTER,
            leading=7,
            fontName='Helvetica',
            fontSize=6
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Center_5',
            alignment=TA_CENTER,
            leading=6,
            fontName='Helvetica',
            fontSize=5
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Left_8',
            alignment=TA_LEFT,
            leading=9,
            fontName='Helvetica',
            fontSize=8
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Left_7',
            alignment=TA_LEFT,
            leading=8,
            fontName='Helvetica',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Left_6',
            alignment=TA_LEFT,
            leading=7,
            fontName='Helvetica',
            fontSize=6
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Left_8',
            alignment=TA_LEFT,
            leading=9,
            fontName='Helvetica-Bold',
            fontSize=8
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Left_7',
            alignment=TA_LEFT,
            leading=8,
            fontName='Helvetica-Bold',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Bold_Left_6',
            alignment=TA_LEFT,
            leading=7,
            fontName='Helvetica-Bold',
            fontSize=6
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Right_7',
            alignment=TA_RIGHT,
            leading=8,
            fontName='Helvetica',
            fontSize=7
        ))
        styles.add(ParagraphStyle(
            name='Helvetica_Right_6',
            alignment=TA_RIGHT,
            leading=7,
            fontName='Helvetica',
            fontSize=6
        ))

        # ========== LOGO ==========
        try:
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'space_black_an_white.png')
            if os.path.exists(logo_path):
                logo_img = Image(logo_path)
                logo_img.drawHeight = 0.9 * inch
                logo_img.drawWidth = 1.0 * inch

                elements.append(logo_img)
                elements.append(Spacer(3, 3))
        except:
            pass

        # ========== ENCABEZADO ACADEMIA ==========
        elements.append(Paragraph('ACADEMIA DE BASQUETBALL', styles['Helvetica_Bold_Center_10']))
        elements.append(Paragraph('SPACE JUMP', styles['Helvetica_Bold_Center_10']))
        elements.append(Spacer(2, 2))
        elements.append(Paragraph('DE: LUIS ANDRE CARRAZCO PINTO', styles['Helvetica_Center_7']))
        elements.append(Spacer(2, 2))
        
        # Información de la academia
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=2, spaceAfter=2))
        elements.append(Paragraph('OFRECEMOS:', styles['Helvetica_Bold_Center_6']))
        elements.append(Paragraph('TALLERES DE BASQUET A NIÑOS Y JÓVENES', styles['Helvetica_Center_6']))
        elements.append(Paragraph('VENTA DE ARTÍCULOS DEPORTIVOS', styles['Helvetica_Center_6']))
        elements.append(Spacer(2, 2))
        elements.append(Paragraph('COOPERATIVA 19 G-6 - PAUCARPATA', styles['Helvetica_Center_5']))
        elements.append(Paragraph('Cel.: 950397123', styles['Helvetica_Center_5']))
        elements.append(Paragraph('Facebook: academia de basquetball space jump', styles['Helvetica_Center_5']))
        elements.append(Paragraph('Email: luisandrecp1@gmail.com', styles['Helvetica_Center_5']))
        elements.append(Spacer(2, 2))
        elements.append(Paragraph('INSCRITA EN REGISTROS PÚBLICOS CON PARTIDA REGISTRAL N° 11541031', styles['Helvetica_Center_5']))
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=2, spaceAfter=2))
        elements.append(Spacer(3, 3))

        # ========== TÍTULO RECIBO ==========
        elements.append(Paragraph('RECIBO', styles['Helvetica_Bold_Center_10']))
        elements.append(Spacer(2, 2))
        # Correlativo con serie de sucursal
        subsidiary_serial = enrollment.subsidiary.serial if enrollment.subsidiary and enrollment.subsidiary.serial else '000'
        receipt_number = f"{subsidiary_serial}-{str(enrollment.id).zfill(6)}"
        elements.append(Paragraph(receipt_number, styles['Helvetica_Center_7']))
        elements.append(Spacer(2, 2))
        
        # Línea separadora
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=5, spaceAfter=3))

        # ========== TABLA DE INFORMACIÓN ==========
        _wt2 = 2.83 * inch - 4 * 0.05 * inch
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        fecha_text = f"{enrollment.enrollment_date.strftime('%d')}/{enrollment.enrollment_date.strftime('%m')}/{enrollment.enrollment_date.strftime('%Y')}"
        
        payment_method_text = {
            'E': 'EFECTIVO',
            'Y': 'YAPE',
            'D': 'DEPÓSITO/TRANSFERENCIA',
            'C': 'CRÉDITO'
        }
        forma_pago = payment_method_text.get(enrollment.payment_method, 'EFECTIVO')
        
        usuario_text = enrollment.user.get_full_name() or enrollment.user.username if enrollment.user else '-'
        
        info_data = []
        info_data.append([
            Paragraph('DEPORTISTA:', styles['Helvetica_Bold_Left_7']),
            Paragraph(enrollment.student.full_name or '-', styles['Helvetica_Left_7'])
        ])
        info_data.append([
            Paragraph('FECHA INSCRIPCIÓN:', styles['Helvetica_Bold_Left_7']),
            Paragraph(fecha_text, styles['Helvetica_Left_7'])
        ])
        info_data.append([
            Paragraph('FORMA DE PAGO:', styles['Helvetica_Bold_Left_7']),
            Paragraph(forma_pago, styles['Helvetica_Left_7'])
        ])
        info_data.append([
            Paragraph('REGISTRADO POR:', styles['Helvetica_Bold_Left_7']),
            Paragraph(usuario_text, styles['Helvetica_Left_7'])
        ])
        
        info_table = Table(info_data, colWidths=[_wt2 * 0.50, _wt2 * 0.50])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(info_table)
        elements.append(Spacer(2, 2))

        # Línea separadora antes de la tabla
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=3, spaceAfter=3))

        # ========== TABLA DE DETALLE ==========
        m_left = 0.00 * inch
        m_right = 0.15 * inch
        _wt2 = 2.83 * inch - m_left - m_right
        
        # Encabezados de la tabla
        table_data_title = [[
            Paragraph("Cant", styles['Helvetica_Bold_Left_6']),
            Paragraph("Descripción", styles['Helvetica_Bold_Left_7']),
            Paragraph("P.U.", styles['Helvetica_Bold_Right_7']),
            Paragraph("Total", styles['Helvetica_Bold_Right_7'])
        ]]
        
        table_title = Table(table_data_title,
                            colWidths=[_wt2 * 10 / 100, _wt2 * 60 / 100, _wt2 * 15 / 100, _wt2 * 15 / 100])
        table_title.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(table_title)
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=0, spaceAfter=1))

        # Detalle de la inscripción
        schedule_days = enrollment.schedule.get_weekdays_display()
        time_slot_text = f"{enrollment.time_slot.start_time.strftime('%H:%M')} - {enrollment.time_slot.end_time.strftime('%H:%M')}"
        description_full = f"{enrollment.cycle.name.upper()}<br/>HORARIO: {enrollment.schedule.name} ({schedule_days})<br/>TURNO: {time_slot_text}"
        
        table_data = [[
            Paragraph("1", styles['Helvetica_Left_7']),
            Paragraph(description_full, styles['Helvetica_Left_7']),
            Paragraph(f"{enrollment.price:.2f}", styles['Helvetica_Right_7']),
            Paragraph(f"{enrollment.price:.2f}", styles['Helvetica_Right_7'])
        ]]
        
        table = Table(table_data,
                      colWidths=[_wt2 * 10 / 100, _wt2 * 60 / 100, _wt2 * 15 / 100, _wt2 * 15 / 100])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(table)
        elements.append(Spacer(2, 2))

        # Línea separadora
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=6, spaceAfter=3))

        # ========== TOTALES ==========
        totales_data = []
        totales_data.append([
            Paragraph("TOTAL:", styles['Helvetica_Bold_Right_7']),
            Paragraph(f"S/ {enrollment.price:.2f}", styles['Helvetica_Right_7'])
        ])
        
        # Solo mostrar adelanto y faltante si no está pagado completo
        if enrollment.remaining > 0:
            totales_data.append([
                Paragraph("ADELANTO:", styles['Helvetica_Bold_Right_7']),
                Paragraph(f"S/ {enrollment.advance:.2f}", styles['Helvetica_Right_7'])
            ])
            totales_data.append([
                Paragraph("PAGO FALTANTE:", styles['Helvetica_Bold_Right_7']),
                Paragraph(f"S/ {enrollment.remaining:.2f}", styles['Helvetica_Bold_Right_7'])
            ])
        
        totales_table = Table(totales_data, colWidths=[_wt2 * 0.6, _wt2 * 0.4])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(2, 2))

        # ========== OBSERVACIONES ==========
        if enrollment.observations:
            elements.append(Paragraph("OBSERVACIONES:", styles['Helvetica_Bold_Left_7']))
            elements.append(Paragraph(enrollment.observations, styles['Helvetica_Left_6']))
            elements.append(Spacer(2, 2))

        # ========== FOOTER ==========
        elements.append(Spacer(3, 3))
        elements.append(HRFlowable(width="100%", thickness=0.3, color="black", spaceBefore=3, spaceAfter=3))
        elements.append(Paragraph("Gracias por su confianza", styles['Helvetica_Bold_Center_6']))

        # Construir el PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    except Exception as e:
        print(f"Error generando PDF de recibo: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def download_enrollment_receipt_pdf(request, enrollment_id):
    """
    Vista para descargar el PDF del recibo de inscripción
    """
    try:
        from .models import Enrollment
        from django.http import HttpResponse

        # Verificar que la inscripción existe
        enrollment = Enrollment.objects.get(id=enrollment_id)

        # Generar el PDF
        pdf_content = generate_enrollment_receipt_pdf(enrollment_id)

        if pdf_content:
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            # Nombre del archivo
            filename = f"RECIBO_{enrollment.student.document_number or enrollment.id}_{enrollment.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse("Error generando el PDF", status=500)

    except Enrollment.DoesNotExist:
        return HttpResponse("Inscripción no encontrada", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)