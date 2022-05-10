from django.db import models


class Student(models.Model):
    first_name = models.CharField(max_length=256, blank=False, verbose_name='First name')
    last_name = models.CharField(max_length=256, blank=False, verbose_name='Last name')
    middle_name = models.CharField(max_length=256, blank=True, verbose_name='Middle name', default='')
    birthday = models.DateField(blank=False, null=True, verbose_name='Birthday')
    photo = models.ImageField(blank=True, null=True, verbose_name='Photo')
    ticket = models.CharField(max_length=256, blank=False, verbose_name='Ticket')
    notes = models.TextField(blank=True, verbose_name='Note')
    student_group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, blank=False)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        permissions = (("can_contact_admin", "Send email to admin"),)

    def __str__(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
