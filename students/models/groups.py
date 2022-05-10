from django.db import models


class Group(models.Model):
    title = models.CharField(max_length=256, verbose_name='Title')
    leader = models.OneToOneField('Student', verbose_name='Leader', blank=True, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        if self.leader:
            return "%s (%s %s)" % (self.title, self.leader.first_name, self.leader.last_name)
        else:
            return "%s" % self.title
