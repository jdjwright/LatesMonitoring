from rest_framework.viewsets import ModelViewSet
from .models import Staff, Student, TutorGroup
from .serializers import StaffSerializer, StudentSerializer, TutorGroupSerializer
from rest_framework.filters import SearchFilter


class StaffViewSet(ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [SearchFilter]
    filterset_fields = ['warehouse_bk']

class TutorGroupViewSet(ModelViewSet):
    queryset = TutorGroup.objects.all()
    serializer_class = TutorGroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [SearchFilter]
    search_fields = ['warehouse_bk']