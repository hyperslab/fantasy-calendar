from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import World, Calendar, TimeUnit


class WorldIndexView(generic.ListView):
    model = World
    template_name = 'fantasycalendar/world_index.html'
    context_object_name = 'world_list'


class WorldDetailView(generic.DetailView):
    model = World
    template_name = 'fantasycalendar/world_detail.html'


class CalendarDetailView(generic.DetailView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'display_unit_type' in self.request.GET:
            context['display_unit'] = TimeUnit.objects.get(pk=self.request.GET['display_unit_type'])
        else:
            context['display_unit'] = TimeUnit.objects.filter(calendar_id=self.object.id).first()
        return context


class WorldCreateView(generic.CreateView):
    model = World
    template_name = 'fantasycalendar/world_create_form.html'
    fields = ['world_name']


class CalendarCreateView(generic.CreateView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_create_form.html'
    fields = ['calendar_name']

    def form_valid(self, form):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        form.instance.world = world
        form.instance.save()
        TimeUnit.objects.create(time_unit_name="Day", calendar=form.instance)
        return super(CalendarCreateView, self).form_valid(form)


class TimeUnitCreateView(generic.CreateView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_create_form.html'
    fields = ['time_unit_name', 'base_unit', 'number_of_base']

    def get_form(self, form_class=None):
        form = super(TimeUnitCreateView, self).get_form()
        form.fields['base_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(TimeUnitCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class WorldUpdateView(generic.UpdateView):
    model = World
    template_name = 'fantasycalendar/world_update_form.html'
    fields = ['world_name']


class CalendarUpdateView(generic.UpdateView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_update_form.html'
    fields = ['calendar_name']


class TimeUnitUpdateView(generic.UpdateView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_update_form.html'
    fields = ['time_unit_name', 'base_unit', 'number_of_base']

    def get_form(self, form_class=None):
        form = super(TimeUnitUpdateView, self).get_form()
        if TimeUnit.objects.get(pk=self.kwargs['pk']).is_bottom_level():
            form.fields['base_unit'].queryset = TimeUnit.objects.none()
        else:
            form.fields['base_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])\
                .exclude(pk=self.kwargs['pk'])
        return form

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})
