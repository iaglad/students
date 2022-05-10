from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import User

from .models import Student, Group, MonthJournal
from .models import StudentProfile


class StudentInline(admin.StackedInline):
    model = Student
    extra = 0


class GroupFormAdmin(ModelForm):
    def clean_leader(self):
        if self.cleaned_data['leader'].student_group != self.instance:
            raise ValidationError('Student in another group', code='invalid')
        return self.cleaned_data['leader']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'leader', 'notes')
    inlines = [StudentInline]
    list_editable = ['leader']
    ordering = ['title']
    list_per_page = 10
    search_fields = ['title', 'leader']
    form = GroupFormAdmin
    def view_on_site(self, obj):
        return reverse('groups_edit', kwargs={'pk': obj.id})


class StudentFormAdmin(ModelForm):
    def clean_student_group(self):
        group = Group.objects.filter(leader=self.instance).first()
        if group and self.cleaned_data['student_group'] != group:
            raise ValidationError('Student is a leader of other group', code='invalid')
        return self.cleaned_data['student_group']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'ticket', 'student_group']
    list_display_links = ['last_name', 'first_name']
    list_editable = ['student_group']
    ordering = ['last_name']
    list_filter = ['student_group']
    list_per_page = 10
    search_fields = ['last_name', 'first_name', 'middle_name', 'ticket', 'notes']
    form = StudentFormAdmin

    def view_on_site(self, obj):
        return reverse('students_edit', kwargs={'pk': obj.id})


admin.site.register(MonthJournal)


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile


class UserAdmin(auth_admin.UserAdmin):
    inlines = (StudentProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)