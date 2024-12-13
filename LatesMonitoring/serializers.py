from rest_framework import serializers
from .models import Staff, Student, TutorGroup

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'first_name', 'last_name', 'preferred_name', 'email', 'warehouse_bk']

class TutorGroupSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())
    head_of_year = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())
    assistant_head = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = TutorGroup
        fields = ['id', 'name', 'tutor', 'head_of_year', 'assistant_head']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'email', 'preferred_name',
            'tutor_group', 'fam_email', 'school_code', 'warehouse_bk'
        ]