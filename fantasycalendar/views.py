from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import World, Calendar, TimeUnit, Event
from django import forms


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
        if 'nest_checkbox' in self.request.GET:
            context['nest_level'] = int(self.request.GET['nest_checkbox'])
        else:
            context['nest_level'] = 0
        if 'iteration' in self.request.GET:
            context['iteration'] = int(self.request.GET['iteration'])
        else:
            context['iteration'] = 1

        if context['nest_level'] > 0 and context['display_unit'].base_unit is not None and \
                context['display_unit'].base_unit.base_unit is not None:
            context['display_nested'] = True
            display_instances = context['display_unit'].get_base_unit_instances(iteration=context['iteration'])
            display_base_names = []
            nested_custom_names = context['display_unit'].base_unit.get_base_unit_instance_names()
            first_base_instance_iteration = context['display_unit'].base_unit.\
                get_first_base_unit_instance_iteration_at_iteration(
                iteration=context['display_unit'].get_first_base_unit_instance_iteration_at_iteration(
                    iteration=context['iteration']))
            for name, length in display_instances:
                nested_display_base_names = []
                for i in range(length):
                    if i < len(nested_custom_names):
                        nested_display_base_name = nested_custom_names[i]
                    else:
                        nested_display_base_name = str(context['display_unit'].base_unit.base_unit.time_unit_name) + \
                                                   ' ' + str(i + 1)
                    events = context['display_unit'].base_unit.base_unit.get_events_at_iteration(
                        iteration=first_base_instance_iteration + i)
                    nested_display_base_names.append((nested_display_base_name, events))
                display_base_names.append((name, nested_display_base_names))
                first_base_instance_iteration += length
            context['display_base_names'] = display_base_names
        else:
            context['display_nested'] = False
            display_amount = int(context['display_unit'].get_length_at_iteration(iteration=context['iteration']))
            if display_amount < 1:
                display_amount = 1
            display_base_names = []
            if context['display_unit'].base_unit is not None:
                custom_names = context['display_unit'].get_base_unit_instance_names()
                first_base_instance_iteration = context['display_unit'].\
                    get_first_base_unit_instance_iteration_at_iteration(iteration=context['iteration'])
                for i in range(1, display_amount + 1):
                    if i - 1 < len(custom_names):
                        display_base_name = custom_names[i - 1]
                    else:
                        display_base_name = str(context['display_unit'].base_unit.time_unit_name) + ' ' + str(i)
                    events = context['display_unit'].base_unit.get_events_at_iteration(
                        iteration=first_base_instance_iteration + (i - 1))
                    display_base_names.append((display_base_name, events))
            else:
                events = context['display_unit'].get_events_at_iteration(iteration=context['iteration'])
                display_base_names.append((context['display_unit'].time_unit_name + ' 1', events))
            context['display_base_names'] = display_base_names

        return context


class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'fantasycalendar/event_detail.html'


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
    fields = ['time_unit_name', 'base_unit', 'length_cycle', 'base_unit_instance_names']

    def get_form(self, form_class=None):
        form = super(TimeUnitCreateView, self).get_form()
        form.fields['base_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        form.fields['base_unit_instance_names'].label = \
            'Enter names of individual base units separated by spaces, if desired'
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(TimeUnitCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class EventCreateView(generic.CreateView):
    model = Event
    template_name = 'fantasycalendar/event_create_form.html'
    fields = ['event_name', 'event_description', 'bottom_level_iteration']

    def get_form(self, form_class=None):
        form = super(EventCreateView, self).get_form()
        bottom_unit = Calendar.objects.get(pk=self.kwargs['calendar_key']).get_bottom_level_time_unit()
        form.fields['bottom_level_iteration'].label = \
            'Which ' + str(bottom_unit.time_unit_name) + ' does this event take place on?'
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(EventCreateView, self).form_valid(form)

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
    fields = ['time_unit_name', 'base_unit', 'length_cycle', 'base_unit_instance_names']

    def get_form(self, form_class=None):
        form = super(TimeUnitUpdateView, self).get_form()
        if TimeUnit.objects.get(pk=self.kwargs['pk']).is_bottom_level():
            form.fields['base_unit'].queryset = TimeUnit.objects.none()
        else:
            form.fields['base_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])\
                .exclude(pk=self.kwargs['pk'])
        form.fields['base_unit_instance_names'].label = \
            'Enter names of individual base units separated by spaces, if desired'
        return form

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class EventUpdateView(generic.UpdateView):
    model = Event
    template_name = 'fantasycalendar/event_update_form.html'
    fields = ['event_name', 'event_description', 'bottom_level_iteration']

    def get_form(self, form_class=None):
        form = super(EventUpdateView, self).get_form()
        bottom_unit = Calendar.objects.get(pk=self.kwargs['calendar_key']).get_bottom_level_time_unit()
        form.fields['bottom_level_iteration'].label = \
            'Which ' + str(bottom_unit.time_unit_name) + ' does this event take place on?'
        return form
