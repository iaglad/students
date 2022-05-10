from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from ..models import Student, Group
from ..util import paginate, get_current_group


class StudentView(TemplateView):
    template_name = 'students/students_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_group = get_current_group(self.request)
        if current_group:
            students = Student.objects.filter(student_group=current_group)
        else:
            students = Student.objects.all()
        order_by = self.request.GET.get('order_by', 'last_name')
        if order_by in ('last_name', 'first_name', 'ticket', 'id'):
            students = students.order_by(order_by)
            if self.request.GET.get('reverse', '') == '1':
                students = students.reverse()
        context = paginate(students, 5, self.request, context, var_name='students')
        return context


class StudentForm(ModelForm):
    class Meta:
        model = Student
        # fields = '__all__'
        fields = ['first_name', 'last_name', 'middle_name', 'birthday', 'photo', 'ticket', 'notes', 'student_group']
        #widgets = {'birthday': DateInput(format="DD.MM.YYYY")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if kwargs['instance']:
            self.helper.form_action = reverse('students_edit', kwargs={'pk': kwargs['instance'].id})
        else:
            self.helper.form_action = reverse('students_add')
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal student-form'
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.label_class = 'col-sm-3 col-form-label'
        self.helper.field_class = 'col-sm-9'
        self.helper['birthday'].wrap(AppendedText, '<i class="bi bi-calendar"></i>')
        self.helper['notes'].wrap(Field, rows=4)
        self.helper.layout.append(FormActions(
            Submit('add_button', 'Save'),
            Submit('cancel_button', 'Cancel', css_class='btn-danger', formnovalidate='formnovalidate', ),
        ))

    def clean_student_group(self):
        group = Group.objects.filter(leader=self.instance).first()
        if group and self.cleaned_data['student_group'] != group:
            raise ValidationError('Student is a leader of other group', code='invalid')
        return self.cleaned_data['student_group']


class StudentBaseView(LoginRequiredMixin):
    model = Student
    template_name = 'students/students_form.html'
    form_class = StudentForm

    def get_success_url(self):
        messages.info(self.request, 'Successfully')
        return reverse('students_list')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel_button'):
            messages.warning(request, 'Canceled')
            return HttpResponseRedirect(reverse('students_list'))
        else:
            return super().post(request, *args, **kwargs)


class StudentUpdateView(StudentBaseView, UpdateView):
    pass


class StudentAddView(StudentBaseView, CreateView):
    pass


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/students_confirm_delete.html'

    def get_success_url(self):
        messages.info(self.request, 'Student deleted!')
        return reverse('students_list')

@login_required
def students_multidel(request):
    if request.method == 'POST':
        if request.POST.get('delete_button') is not None:
            items = request.POST.getlist('for_del')
            print(items)
            for student in Student.objects.filter(id__in=items):
                student.delete()
            messages.info(request, 'Students are deleted')
            return HttpResponseRedirect(reverse('students_list'))
        elif request.POST.get('cancel_button') is not None:
            messages.info(request, 'Delete canceled')
            return HttpResponseRedirect(reverse('students_list'))
        else:
            items = request.POST.getlist('checks[]')
            print(items)
            if items:
                students = Student.objects.filter(id__in=items)
                return render(request, 'students/students_multidel.html', {'students': students})
            else:
                return HttpResponseRedirect(reverse('students_list'))
    #else:
    #    return HttpResponseRedirect(reverse('students_list'))

# def students_add(request):
#     groups = Group.objects.all().order_by('title')
#     if request.method == "POST":
#         if request.POST.get('add_button') is not None:
#             data = {'middle_name': request.POST.get('middle_name'), 'notes': request.POST.get('notes')}
#             first_name = request.POST.get('first_name', '').strip()
#             if not first_name:
#                 messages.add_message(request, messages.ERROR, 'имя обязательно')
#             else:
#                 data['first_name'] = first_name
#             last_name = request.POST.get('last_name', '').strip()
#             if not last_name:
#                 messages.add_message(request, messages.ERROR, 'фамилия обязательна')
#             else:
#                 data['last_name'] = last_name
#             birthday = request.POST.get('birthday', '').strip()
#             if not birthday:
#                 messages.add_message(request, messages.ERROR, 'ДР обязательна')
#             else:
#                 try:
#                     datetime.strptime(birthday, '%Y-%m-%d')
#                 except Exception:
#                     messages.add_message(request, messages.ERROR, 'ДР %Y-%m-%d')
#                 else:
#                     data['birthday'] = birthday
#             ticket = request.POST.get('ticket', '').strip()
#             if not ticket:
#                 messages.add_message(request, messages.ERROR, 'билет обязателен')
#             else:
#                 data['ticket'] = ticket
#             student_group = request.POST.get('student_group', '').strip()
#             if not student_group:
#                 messages.add_message(request, messages.ERROR, 'выберите группу')
#             else:
#                 group = Group.objects.filter(pk=student_group).first()
#                 if group:
#                     data['student_group'] = group
#                 else:
#                     messages.add_message(request, messages.ERROR, 'выберите корректную группу')
#             photo = request.FILES.get('photo')
#             photoerror = False
#             if photo:
#                 if photo.size > 2048000:
#                     messages.add_message(request, messages.ERROR, 'size of photo > 2mb')
#                     photoerror = True
#                 else:
#                     if imghdr.what(photo) is None:
#                         messages.add_message(request, messages.ERROR, 'photo is not image')
#                         photoerror = True
#                 if not photoerror:
#                     data['photo'] = photo
#
#             if len(list(messages.get_messages(request))) == 0:
#                 student = Student(**data)
#                 student.save()
#                 s = student.last_name + ' ' + student.first_name + ' успішно додан(а)!'
#                 messages.add_message(request, messages.INFO, s)
#                 return HttpResponseRedirect(reverse('students_list'))
#             else:
#                 return render(request, 'students/students_add.html', {'groups': groups})
#         elif request.POST.get('cancel_button') is not None:
#             messages.add_message(request, messages.WARNING, 'Додавання студента скасовано!!')
#             return HttpResponseRedirect(reverse('students_list'))
#     else:
#         return render(request, 'students/students_add.html', {'groups': groups})

# def students_list(request):
#     students = Student.objects.all()
#     order_by = request.GET.get('order_by', 'last_name')
#     if order_by in ('last_name', 'first_name', 'ticket', 'id'):
#         students = students.order_by(order_by)
#         if request.GET.get('reverse', '') == '1':
#             students = students.reverse()
# paginator
# paginator = Paginator(students, 5)
# page = request.GET.get('page')
# try:
#     students = paginator.page(page)
# except PageNotAnInteger:
#     students = paginator.page(1)
# except EmptyPage:
#     students = paginator.page(paginator.num_pages)
# return render(request, 'students/students_list.html', {'students': students})
