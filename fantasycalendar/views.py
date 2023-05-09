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
        display_amount = int(context['display_unit'].number_of_base)
        if display_amount < 1:
            display_amount = 1
        display_base_names = []
        if context['display_unit'].base_unit is not None:
            custom_names = context['display_unit'].get_base_unit_instance_names()
            for i in range(1, display_amount + 1):
                if i - 1 < len(custom_names):
                    display_base_names.append(custom_names[i - 1])
                else:
                    display_base_names.append(str(context['display_unit'].base_unit.time_unit_name) + ' ' + str(i))
        else:
            display_base_names.append(context['display_unit'].time_unit_name + ' 1')
        context['display_base_names'] = display_base_names
        if 'nest_checkbox' in self.request.GET:
            context['nest_level'] = int(self.request.GET['nest_checkbox'])
        else:
            context['nest_level'] = 0
        if context['nest_level'] > 0 and context['display_unit'].base_unit is not None and \
                context['display_unit'].base_unit.base_unit is not None:
            context['display_nested'] = True
            nested_display_base_names = []
            nested_custom_names = context['display_unit'].base_unit.get_base_unit_instance_names()
            for i in range(1,  int(context['display_unit'].base_unit.number_of_base) + 1):
                if i - 1 < len(nested_custom_names):
                    nested_display_base_names.append(nested_custom_names[i - 1])
                else:
                    nested_display_base_names.append(str(context['display_unit'].base_unit.base_unit.time_unit_name) + ' ' + str(i))
            context['nested_display_base_names'] = nested_display_base_names
        else:
            context['display_nested'] = False
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
