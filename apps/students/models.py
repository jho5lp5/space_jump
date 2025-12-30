from django.db import models

# Create your models here.
from django.db import models

from apps import hrm, users


class Student(models.Model):
    """Model for athletes of SPACE JUMP academy"""
    DOCUMENT_CHOICES = (
        ('01', 'DNI'), ('06', 'RUC'))

    id = models.AutoField(primary_key=True)
    # Personal data
    document = models.CharField('Tipo Documento', max_length=2, choices=DOCUMENT_CHOICES, default='01')
    document_number = models.CharField('Número de Documento', max_length=15, null=True, blank=True)
    first_name = models.CharField('Primer Nombre', max_length=200, null=True, blank=True)
    second_name = models.CharField('Segundo Nombre', max_length=200, null=True, blank=True)
    surname = models.CharField('Primer Apellido', max_length=200, null=True, blank=True)
    second_surname = models.CharField('Segundo Apellido', max_length=200, null=True, blank=True)
    full_name = models.CharField('Nombres y Apellidos', max_length=200, null=True, blank=True)
    birth_place = models.CharField('Lugar de Nacimiento', max_length=200, null=True, blank=True)
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    address = models.CharField('Domicilio', max_length=200, null=True, blank=True)
    phone = models.CharField('Teléfono Celular', max_length=15, null=True, blank=True)
    photo = models.ImageField('Foto', upload_to='students/', null=True, blank=True)

    # Parent/guardian data
    parent_first_name = models.CharField('Nombres del Padre/Madre/Apoderado', max_length=200, null=True, blank=True)
    parent_surname = models.CharField('Apellidos del Padre/Madre/Apoderado', max_length=200, null=True, blank=True)
    parent_document = models.CharField('Tipo Documento del Padre/Madre/Apoderado', max_length=2,
                                       choices=DOCUMENT_CHOICES, default='01', null=True, blank=True)
    parent_document_number = models.CharField('Número de Documento del Padre/Madre/Apoderado', max_length=15, null=True,
                                              blank=True)
    parent_phone = models.CharField('Teléfono del Padre/Madre/Apoderado', max_length=15, null=True, blank=True)

    # Medical history
    diseases = models.TextField('Enfermedades', max_length=500, null=True, blank=True)
    medication_allergies = models.TextField('Alergia a Medicamentos', max_length=500, null=True, blank=True)
    student_insurance = models.CharField('Seguro del Estudiante', max_length=200, null=True, blank=True)
    sports_injuries = models.TextField('Lesiones Deportivas', max_length=500, null=True, blank=True)
    other_medical_info = models.TextField('Otros', max_length=500, null=True, blank=True)

    # Additional info
    current_age = models.IntegerField('Edad Actual', null=True, blank=True)
    subsidiary = models.ForeignKey('hrm.Subsidiary', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Sede')
    observations = models.TextField('Observaciones', max_length=500, null=True, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    creation_date = models.DateTimeField('Fecha de Creación', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.full_name or f"{self.first_name} {self.surname}")

    def save(self, *args, **kwargs):
        if not self.full_name:
            name_parts = [self.first_name, self.second_name, self.surname, self.second_surname]
            self.full_name = ' '.join([part for part in name_parts if part])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['-creation_date']


class Cycle(models.Model):
    """Model for training cycles (e.g., Summer Cycle 2026)"""
    DURATION_CHOICES = (
        (1, '1 mes'),
        (2, '2 meses'),
        (3, '3 meses'),
        (6, '6 meses'),
        (12, 'Anual'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField('Nombre del Ciclo', max_length=150, help_text='Ej: Ciclo Verano 2026')
    start_date = models.DateField('Fecha de Inicio', null=True, blank=True)
    end_date = models.DateField('Fecha de Fin', null=True, blank=True)
    duration_months = models.IntegerField('Duración en Meses', choices=DURATION_CHOICES, default=1)
    is_active = models.BooleanField('Activo', default=True)
    creation_date = models.DateTimeField('Fecha de Creación', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.duration_months} mes{'es' if self.duration_months > 1 else ''})"

    class Meta:
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'
        ordering = ['-creation_date']


class TrainingSchedule(models.Model):
    """Model for training schedules/plans within a cycle (days of the week)"""
    id = models.AutoField(primary_key=True)
    cycle = models.ForeignKey('Cycle', on_delete=models.CASCADE, related_name='schedules', verbose_name='Ciclo')
    name = models.CharField('Nombre', max_length=150, help_text='Ej: Interdiario, Diario')
    monday = models.BooleanField('Lunes', default=False)
    tuesday = models.BooleanField('Martes', default=False)
    wednesday = models.BooleanField('Miércoles', default=False)
    thursday = models.BooleanField('Jueves', default=False)
    friday = models.BooleanField('Viernes', default=False)
    saturday = models.BooleanField('Sábado', default=False)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('Activo', default=True)
    creation_date = models.DateTimeField('Fecha de Creación', auto_now_add=True, null=True, blank=True)

    def get_weekdays_display(self):
        days = []
        if self.monday: days.append('Lun')
        if self.tuesday: days.append('Mar')
        if self.wednesday: days.append('Mié')
        if self.thursday: days.append('Jue')
        if self.friday: days.append('Vie')
        if self.saturday: days.append('Sáb')
        return ', '.join(days) if days else 'Sin días'

    def __str__(self):
        return f"{self.name} - {self.get_weekdays_display()}"

    class Meta:
        verbose_name = 'Horario de Entrenamiento'
        verbose_name_plural = 'Horarios de Entrenamiento'
        ordering = ['cycle', 'name']


class TimeSlot(models.Model):
    """Model for time slots/turns within a schedule"""
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey('TrainingSchedule', on_delete=models.CASCADE, related_name='time_slots',
                                 verbose_name='Horario')
    start_time = models.TimeField('Hora de Inicio')
    end_time = models.TimeField('Hora de Fin')
    age_description = models.CharField('Descripción de Edad', max_length=200, null=True, blank=True,
                                       help_text='Ej: Alumnos de 13 a 17 años')
    capacity = models.IntegerField('Capacidad', default=20, null=True, blank=True)
    teacher = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Profesor', related_name='time_slots',
                                limit_choices_to={'type_employee': '2'})
    is_active = models.BooleanField('Activo', default=True)
    creation_date = models.DateTimeField('Fecha de Creación', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} ({self.age_description or 'Todas las edades'})"

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['schedule', 'start_time']


class Enrollment(models.Model):
    """Model for enrolling students to cycles, schedules and time slots"""
    PAYMENT_METHOD_CHOICES = (
        ('E', 'Efectivo'),
        ('Y', 'Yape'),
        ('D', 'Depósito/Transferencia'),
        ('C', 'Crédito'),
    )
    STATUS_CHOICES = (
        ('A', 'Activo'),
        ('V', 'Vencido'),
        ('C', 'Cancelado'),
        ('P', 'Pendiente'),
    )

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='enrollments',
                                verbose_name='Deportista')
    cycle = models.ForeignKey('Cycle', on_delete=models.CASCADE, verbose_name='Ciclo')
    schedule = models.ForeignKey('TrainingSchedule', on_delete=models.CASCADE, verbose_name='Horario')
    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, verbose_name='Turno')
    enrollment_date = models.DateField('Fecha de Inscripción')
    price = models.DecimalField('Precio Total', max_digits=10, decimal_places=2, default=0)
    advance = models.DecimalField('Adelanto', max_digits=10, decimal_places=2, default=0)
    remaining = models.DecimalField('Faltante', max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField('Método de Pago', max_length=1, choices=PAYMENT_METHOD_CHOICES, default='E')
    status = models.CharField('Estado', max_length=1, choices=STATUS_CHOICES, default='P')
    subsidiary = models.ForeignKey('hrm.Subsidiary', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Sede')
    user = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Registrado por')
    observations = models.TextField('Observaciones', max_length=500, null=True, blank=True)
    creation_date = models.DateTimeField('Fecha de Creación', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.cycle.name}"

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-enrollment_date', '-creation_date']
