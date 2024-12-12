from django.contrib import admin
from .models import Person, Staff, TutorGroup, Student, DetentionType, Detention, StudentInDetention

# Base Person Admin
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'preferred_name', 'email', 'warehouse_bk')
    search_fields = ('first_name', 'last_name', 'email')

# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'warehouse_bk')
    search_fields = ('first_name', 'last_name', 'email')

# TutorGroup Admin
@admin.register(TutorGroup)
class TutorGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'tutor', 'head_of_year', 'assistant_head')
    search_fields = ('name', 'tutor__first_name', 'tutor__last_name')
    autocomplete_fields = ('tutor', 'head_of_year', 'assistant_head')

# Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'tutor_group')
    search_fields = ('first_name', 'last_name', 'email', 'tutor_group__name')
    autocomplete_fields = ('tutor_group',)

# DetentionType Admin
@admin.register(DetentionType)
class DetentionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_colour', 'severity', 'default_room', 'default_staff', 'first_date_and_time')
    search_fields = ('name',)
    list_filter = ('severity',)
    autocomplete_fields = ('default_staff',)

# Detention Admin
@admin.register(Detention)
class DetentionAdmin(admin.ModelAdmin):
    list_display = ('detention_type', 'room', 'date_and_time')
    search_fields = ('detention_type__name', 'room')
    autocomplete_fields = ('detention_type', 'staff')
    filter_horizontal = ('staff',)

# StudentInDetention Admin
@admin.register(StudentInDetention)
class StudentInDetentionAdmin(admin.ModelAdmin):
    list_display = ('student', 'detention', 'authorised', 'total_lates', 'attendance')
    search_fields = ('student__first_name', 'student__last_name', 'detention__detention_type__name')
    list_filter = ('attendance', 'authorised')
    autocomplete_fields = ('student', 'detention')
