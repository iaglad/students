from django.views.generic import TemplateView
from django.contrib.auth.models import User

from students.util import paginate


class ProfileView(TemplateView):
    template_name = 'profiles/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)
        try:
            profile_user = User.objects.get(pk=kwargs['pk'])
            context['user'] = user
            context['profile_user'] = profile_user
        except Exception:
            pass
        return context


class UsersListView(TemplateView):
    template_name = 'profiles/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        order_by = self.request.GET.get('order_by', 'username')
        if order_by in ('id', 'username'):
            users = users.order_by(order_by)
            if self.request.GET.get('reverse', '') == '1':
                users = users.reverse()

        context = paginate(users, 5, self.request, context, var_name='users')
        return context
