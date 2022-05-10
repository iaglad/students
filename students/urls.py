from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include
from django.views.generic import TemplateView

from students.views import groups, students, journal, contact_admin, profiles


urlpatterns = [
    path('', students.StudentView.as_view(), name='students_list'),
    path('students/add/', students.StudentAddView.as_view(), name='students_add'),
    path('students/multidel/', students.students_multidel, name='students_multidel'),
    path('students/<int:pk>/edit/', students.StudentUpdateView.as_view(), name='students_edit'),
    path('students/<int:pk>/delete/', students.StudentDeleteView.as_view(), name='students_delete'),

    path('groups/', groups.GroupView.as_view(), name='groups_list'),
    path('groups/add/', groups.GroupAddView.as_view(), name='groups_add'),
    path('groups/<int:pk>/edit/', groups.GroupUpdateView.as_view(), name='groups_edit'),
    path('groups/<int:pk>/delete/', groups.GroupDeleteView.as_view(), name='groups_delete'),

    re_path(r'journal/(?:(?P<pk>\d+)/)?$', login_required(journal.JournalView.as_view()), name='journal'),

    path('contact_admin/', contact_admin.contact_admin, name='contact_admin'),

    path('accounts/profile/', login_required(TemplateView.as_view(template_name='profiles/profile.html')),
         name='profile'),
    path('accounts/users/', login_required(profiles.UsersListView.as_view()), name='users_list'),
    path('accounts/profile/<int:pk>/', login_required(profiles.ProfileView.as_view()), name='profile_id'),
    path('accounts/', include('allauth.urls')),
]
