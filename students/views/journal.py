from datetime import datetime, date
from calendar import monthrange, weekday, day_abbr
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic.base import TemplateView

from students.models import Student, MonthJournal
from students.util import paginate, get_current_group


class JournalView(TemplateView):
    template_name = 'students/journal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_group = get_current_group(self.request)
        if self.request.GET.get('month'):
            month = datetime.strptime(self.request.GET['month'], '%Y-%m-%d').date()
        else:
            today = datetime.today()
            month = date(today.year, today.month, 1)
        next_month = month + relativedelta(months=1)
        prev_month = month - relativedelta(months=1)
        context['prev_month'] = prev_month.strftime('%Y-%m-%d')
        context['next_month'] = next_month.strftime('%Y-%m-%d')
        context['year'] = month.year
        context['cur_month'] = month.strftime('%Y-%m-%d')
        context['month_verbose'] = month.strftime('%B')
        myear, mmonth = month.year, month.month
        number_of_days = monthrange(myear, mmonth)[1]
        context['month_header'] = [
            {'day': d, 'verbose': day_abbr[weekday(myear, mmonth, d)][:2]}
            for d in range(1, number_of_days + 1)]

        # if kwargs.get('pk'):
        #     if current_group and Student.objects.get(pk=kwargs['pk']).student_group == current_group:
        #         try:
        #             queryset = [Student.objects.filter(student_group=current_group).get(pk=kwargs['pk'])]
        #         except:
        #             queryset = []
        #     else:
        #         queryset = Student.objects.order_by('last_name')
        # else:
        #     queryset = Student.objects.order_by('last_name')
        #     if current_group:
        #         queryset = queryset.filter(student_group=current_group)
        if current_group:
            queryset = Student.objects.filter(student_group=current_group)
        else:
            queryset = Student.objects.order_by('last_name')
        if kwargs.get('pk'):
            if not current_group or Student.objects.get(pk=kwargs['pk']).student_group == current_group:
                queryset = [Student.objects.get(pk=kwargs['pk'])]
            else:
                queryset = []

        update_url = reverse('journal')
        students = []
        for student in queryset:
            journal = (MonthJournal.objects.filter(student=student, date=month).first())
            days = []
            for day in range(1, number_of_days + 1):
                days.append({
                    'day': day,
                    'present': journal and getattr(journal, 'present_day%d' % day, False) or False,
                    'date': date(myear, mmonth, day).strftime('%Y-%m-%d'),
                })
            students.append({
                'fullname': '%s %s' % (student.last_name, student.first_name),
                'days': days,
                'id': student.id,
                'update_url': update_url,
            })
        context = paginate(students, 5, self.request, context, var_name='students')
        return context


    @login_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        current_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        month = date(current_date.year, current_date.month, 1)
        present = data['present'] and True or False
        student = Student.objects.get(pk=data['pk'])
        journal, created = MonthJournal.objects.get_or_create(student=student, date=month)
        setattr(journal, 'present_day%d' % current_date.day, present)
        journal.save()
        return JsonResponse({'status': 'success'})