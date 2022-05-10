from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError

from ..models import Group
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, DeleteView, TemplateView
#  -----   group ------------------------
from ..util import paginate, get_current_group


class GroupView(TemplateView):
    template_name = 'students/groups_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_group = get_current_group(self.request)
        if current_group:
            groups = Group.objects.filter(pk=current_group.pk)
        else:
            groups = Group.objects.all()
        order_by = self.request.GET.get('order_by', 'title')
        if order_by in ('title', 'leader'):
            groups = groups.order_by(order_by)
            if self.request.GET.get('reverse', '') == '1':
                groups = groups.reverse()
        context = paginate(groups, 5, self.request, context, var_name='groups')
        return context


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if kwargs['instance']:
            self.helper.form_action = reverse('groups_edit', kwargs={'pk': kwargs['instance'].id})
        else:
            self.helper.form_action = reverse('groups_add')
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.label_class = 'col-sm-2 col-form-label'
        self.helper.field_class = 'col-sm-10'
        self.helper.layout.append(FormActions(
            Submit('add_button', 'Save'),
            Submit('cancel_button', 'Cancel', css_class='btn-danger', formnovalidate='formnovalidate',),
        ))

    def clean_leader(self):
        if self.cleaned_data['leader'].student_group != self.instance:
            raise ValidationError('Student in another group', code='invalid')
        return self.cleaned_data['leader']


class GroupBaseView(LoginRequiredMixin):
    model = Group
    template_name = 'students/groups_form.html'
    form_class = GroupForm

    def get_success_url(self):
        messages.info(self.request, 'Successfully')
        return reverse('groups_list')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel_button'):
            messages.warning(request, 'Canceled')
            return HttpResponseRedirect(reverse('groups_list'))
        else:
            return super().post(request, *args, **kwargs)


class GroupUpdateView(GroupBaseView, UpdateView):
    pass


class GroupAddView(GroupBaseView, CreateView):
    pass


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'students/groups_confirm_delete.html'

    def get_success_url(self):
        messages.info(self.request, 'Group deleted!')
        return reverse('groups_list')


# def groups_list(request):
#     groups = Group.objects.all()
#     order_by = request.GET.get('order_by', 'title')
#     if order_by in ('title', 'leader'):
#         groups = groups.order_by(order_by)
#         if request.GET.get('reverse', '') == '1':
#             groups = groups.reverse()
#     # paginator
#     paginator = Paginator(groups, 3)
#     page = request.GET.get('page')
#     try:
#         groups = paginator.page(page)
#     except PageNotAnInteger:
#         groups = paginator.page(1)
#     except EmptyPage:
#         groups = paginator.page(paginator.num_pages)
#     return render(request, 'students/groups_list.html', {'groups': groups})
