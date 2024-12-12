from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    preferred_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    warehouse_bk = models.IntegerField()

class Staff(Person):
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class TutorGroup(models.Model):
    name = models.CharField(max_length=4)
    tutor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='tutors')
    head_of_year = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='head_of_year')
    assistant_head = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='assistant_head')

class Student(Person):
    tutor_group = models.ForeignKey(TutorGroup, on_delete=models.CASCADE)
    school_id = models.IntegerField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.tutor_group.name})'


class DetentionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_colour = models.CharField(max_length=7, help_text="A hex colour to represnt this detention")
    severity = models.IntegerField(help_text="The severity of this detention. Higher is more severe")
    default_room = models.CharField(max_length=50, help_text="The default room of this detention")
    default_staff = models.ForeignKey(Staff, on_delete=models.CASCADE,
                                      help_text="The default staff of this detention",
                                      null=True, blank=True)
    first_date_and_time = models.DateTimeField(help_text="The first date and time of this detention. Future detentions will be on the same day of the week")

    def __str__(self):
        return f'{self.name}'


class Detention(models.Model):
    detention_type = models.ForeignKey(DetentionType, on_delete=models.CASCADE)
    room = models.CharField(max_length=50, help_text="The room of this detention")
    staff = models.ManyToManyField(Staff)
    date_and_time = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return f'{self.detention_type.name} - {str(self.date_and_time.date())}'

    def students(self):
        return self.students().all

class StudentInDetention(models.Model):
    class AttendanceChoices(models.TextChoices):
        ATTENDED = "\\", "Attended"
        ABSENT_WITH_REASON = 'V', "Absent with reason"
        ABSENT_NO_REASON = "N", "Absent no reason"
        NOT_RECORDED = "-", "Not recorded"

    detention = models.ForeignKey(Detention, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    authorised = models.BooleanField(default=True)
    total_lates = models.IntegerField(help_text="The total number of lates that lead to this detention")
    attendance = models.TextField(choices=AttendanceChoices.choices, blank=True, default=AttendanceChoices.NOT_RECORDED)

    def __str__(self):
        return f'{str(self.student)} - {str(self.detention)}'




