from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import (World, Calendar, TimeUnit, Event, EventGroup, DateFormat, DisplayConfig, DateBookmark,
                     DisplayUnitConfig)
from .forms import (DisplayConfigCreateForm, DisplayConfigUpdateForm, DisplayUnitConfigCreateForm,
                    DisplayUnitConfigUpdateForm, DateBookmarkCreateForm, CalendarUpdateForm, EventGroupDeleteForm)


class WorldIndexView(generic.ListView):
    model = World
    template_name = 'fantasycalendar/world_index.html'
    context_object_name = 'world_list'

    def get_queryset(self):
        worlds = World.objects.filter(public=True)
        if self.request.user.is_authenticated:
            worlds = worlds.exclude(creator_id=self.request.user.id)
        return worlds

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WorldIndexView, self).get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_authenticated:
            context['user_world_list'] = World.objects.filter(creator_id=self.request.user.id)
        return context


class WorldDetailView(UserPassesTestMixin, generic.DetailView):
    model = World
    template_name = 'fantasycalendar/world_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['pk'])
        return world.public or self.request.user == world.creator


class CalendarDetailView(UserPassesTestMixin, generic.DetailView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'display_unit' in self.request.GET:
            context['display_unit'] = TimeUnit.objects.get(pk=self.request.GET['display_unit'])
        elif self.object.default_display_config:
            context['display_unit'] = self.object.default_display_config.default_display_unit_config.time_unit
        else:
            self.object.ensure_bottom_level_time_unit()  # if unit not specified, it might not have one yet
            context['display_unit'] = TimeUnit.objects.filter(calendar_id=self.object.id).first()
        if 'display_sub_unit' in self.request.GET:
            context['display_sub_unit'] = TimeUnit.objects.get(pk=self.request.GET['display_sub_unit'])
        elif self.object.default_display_config:
            context['display_sub_unit'] = self.object.default_display_config.default_display_unit_config.sub_unit
        else:
            self.object.ensure_bottom_level_time_unit()  # if unit not specified, it might not have one yet
            context['display_sub_unit'] = TimeUnit.objects.filter(calendar_id=self.object.id).first()
        if 'iteration' in self.request.GET:
            context['iteration'] = int(self.request.GET['iteration'])
        elif self.object.default_display_config and self.object.default_display_config.default_date_bookmark:
            context['iteration'] = self.object.default_display_config.default_date_bookmark.bookmark_iteration
        else:
            context['iteration'] = 1

        return context


class CalendarCalendarView(UserPassesTestMixin, generic.DetailView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_calendar.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator


class TimeUnitDetailView(UserPassesTestMixin, generic.DetailView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator


class TimeUnitInstanceDetailView(UserPassesTestMixin, generic.DetailView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_instance_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['iteration'] = self.kwargs['iteration']
        context['first_bottom_level_iteration'] = self.object.get_first_bottom_level_iteration_at_iteration(
            iteration=self.kwargs['iteration'])
        context['events'] = self.object.get_events_at_iteration(iteration=self.kwargs['iteration'])
        context['date_bookmarks'] = DateBookmark.objects.filter(bookmark_unit_id=self.object.id).\
            filter(bookmark_iteration=self.kwargs['iteration'])
        if self.object.default_date_format:
            context['display_name'] = self.object.default_date_format.get_formatted_date(self.kwargs['iteration'])
        else:
            context['display_name'] = str(self.object.time_unit_name) + ' ' + str(self.kwargs['iteration'])
        date_formats = DateFormat.objects.filter(time_unit_id=self.object.id)
        formatted_dates = [d.get_formatted_date(self.kwargs['iteration']) for d in date_formats]
        context['date_representations'] = [(df, fd) for df, fd in zip(date_formats, formatted_dates)]
        context['is_linked'] = self.object.is_linked()
        linked_instances = self.object.get_linked_instance_iterations(self.kwargs['iteration'])
        context['linked_instances'] = [(calendar.id, calendar.calendar_name, calendar.get_bottom_level_time_unit().id,
                                        iteration,
                                        calendar.get_bottom_level_time_unit().get_instance_display_name(iteration))
                                       for (calendar, iteration) in linked_instances]
        return context


class EventDetailView(UserPassesTestMixin, generic.DetailView):
    model = Event
    template_name = 'fantasycalendar/event_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bottom_level_time_unit = self.object.calendar.get_bottom_level_time_unit()
        if bottom_level_time_unit.default_date_format:
            context['display_date'] = bottom_level_time_unit.default_date_format.\
                get_formatted_date(self.object.bottom_level_iteration)
        else:
            context['display_date'] = str(bottom_level_time_unit.time_unit_name) + ' ' + \
                                      str(self.object.bottom_level_iteration)
        context['time_unit'] = bottom_level_time_unit
        return context


class EventGroupDetailView(UserPassesTestMixin, generic.DetailView):
    model = EventGroup
    template_name = 'fantasycalendar/event_group_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events_sorted'] = Event.objects.filter(event_group_id=self.object.id).order_by(
            'bottom_level_iteration', 'display_order')
        return context


class DateFormatDetailView(UserPassesTestMixin, generic.DetailView):
    model = DateFormat
    template_name = 'fantasycalendar/date_format_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator


class DisplayConfigDetailView(UserPassesTestMixin, generic.DetailView):
    model = DisplayConfig
    template_name = 'fantasycalendar/display_config_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unused_unit_configs = self.object.get_unused_display_unit_configs()
        context['can_add_unit_configs'] = True if len(unused_unit_configs) > 0 else False
        return context


class WorldCreateView(LoginRequiredMixin, generic.CreateView):
    model = World
    template_name = 'fantasycalendar/world_create_form.html'
    fields = ['world_name', 'public']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.save()
        return super(WorldCreateView, self).form_valid(form)


class CalendarCreateView(UserPassesTestMixin, generic.CreateView):
    model = Calendar
    template_name = 'fantasycalendar/calendar_create_form.html'
    fields = ['calendar_name', 'world_link_iteration']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def form_valid(self, form):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        form.instance.world = world
        form.instance.save()
        form.instance.ensure_bottom_level_time_unit()
        form.instance.ensure_default_display_config()
        return super(CalendarCreateView, self).form_valid(form)


class TimeUnitCreateView(UserPassesTestMixin, generic.CreateView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_create_form.html'
    fields = ['time_unit_name', 'base_unit', 'length_cycle', 'base_unit_instance_names']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

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


class EventCreateView(UserPassesTestMixin, generic.CreateView):
    model = Event
    template_name = 'fantasycalendar/event_create_form.html'
    fields = ['event_name', 'event_description', 'bottom_level_iteration', 'display_order', 'event_group', 'visible']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_initial(self):
        if 'bottom_level_iteration' in self.request.GET:
            return {'bottom_level_iteration': int(self.request.GET['bottom_level_iteration'])}

    def get_form(self, form_class=None):
        form = super(EventCreateView, self).get_form()
        bottom_unit = Calendar.objects.get(pk=self.kwargs['calendar_key']).get_bottom_level_time_unit()
        form.fields['bottom_level_iteration'].label = \
            'Which ' + str(bottom_unit.time_unit_name) + ' does this event take place on?'

        class ModelChoiceFieldWithVisibility(forms.ModelChoiceField):
            def label_from_instance(self, obj):
                return obj.__str__() + ' (' + ('not ' if not obj.visible else '') + 'visible)'

        form.fields['event_group'] = ModelChoiceFieldWithVisibility(required=False,
            queryset=EventGroup.objects.filter(calendar_id=self.kwargs['calendar_key']))
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(EventCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:time-unit-instance-detail',
                       kwargs={'world_key': self.object.calendar.world.pk,
                               'calendar_key': self.object.calendar.pk,
                               'pk': self.object.calendar.get_bottom_level_time_unit().pk,
                               'iteration': self.object.bottom_level_iteration})


class EventGroupCreateView(UserPassesTestMixin, generic.CreateView):
    model = EventGroup
    template_name = 'fantasycalendar/event_group_create_form.html'
    fields = ['event_group_name', 'visible']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(EventGroupCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class DateFormatCreateView(UserPassesTestMixin, generic.CreateView):
    model = DateFormat
    template_name = 'fantasycalendar/date_format_create_form.html'
    fields = ['date_format_name', 'format_string']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        units_and_parents = []
        for unit in TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key']):
            units_and_parents.append((unit, unit.get_all_higher_containing_units()))
        context['units_and_parents'] = units_and_parents
        return context

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        time_unit = get_object_or_404(TimeUnit, pk=self.kwargs['timeunit_key'])
        form.instance.calendar = calendar
        form.instance.time_unit = time_unit
        return super(DateFormatCreateView, self).form_valid(form)


class DisplayConfigCreateView(UserPassesTestMixin, generic.CreateView):
    model = DisplayConfig
    form_class = DisplayConfigCreateForm
    template_name = 'fantasycalendar/display_config_create_form.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(DisplayConfigCreateView, self).get_form()

        # provide default name if this is the calendar's first display config
        if not DisplayConfig.objects.filter(calendar_id=self.kwargs['calendar_key']).exists():
            form['display_config_name'].initial = 'Default Display Config'

        possible_unit_configs = []
        for unit in TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key']):
            possible_unit_configs.append((unit, None))
            for parent_unit in unit.get_all_higher_containing_units():
                possible_unit_configs.append((parent_unit, unit))
        form.fields['default_time_unit_page'].choices = \
            [(str(uc[0].pk) + ',' + (str(uc[1].pk) if uc[1] is not None else ''),
              'All ' + uc[1].time_unit_name + ' in a ' + uc[0].time_unit_name if uc[1] is not None else
              'Single ' + uc[0].time_unit_name)
             for uc in possible_unit_configs]

        form.fields['default_date_bookmark'].queryset = DateBookmark.objects.filter(
            calendar_id=self.kwargs['calendar_key'], personal_bookmark_creator=None)

        form.order_fields(['display_config_name', 'default_time_unit_page', 'default_date_bookmark'])

        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        instance = form.save(commit=False)

        time_unit_key = form.cleaned_data['default_time_unit_page'].split(',')[0]
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_key)
        sub_unit_key = form.cleaned_data['default_time_unit_page'].split(',')[1]
        sub_unit = None
        if sub_unit_key:
            sub_unit = get_object_or_404(TimeUnit, pk=sub_unit_key)
        default_display_unit_config = DisplayUnitConfig(
            display_config=instance, time_unit=time_unit, sub_unit=sub_unit)

        with transaction.atomic():
            instance.save()
            default_display_unit_config.save()
            instance.default_display_unit_config = default_display_unit_config
            instance.save()

        # set as calendar default if this is the calendar's first display config
        if DisplayConfig.objects.filter(calendar_id=self.kwargs['calendar_key']).count() == 1:
            calendar.default_display_config = form.instance
            calendar.save()

        return super(DisplayConfigCreateView, self).form_valid(form)

    def get_success_url(self):
        # show calendar page instead of detail page if this is the calendar's first display config
        if DisplayConfig.objects.filter(calendar_id=self.kwargs['calendar_key']).count() == 1:
            return reverse('fantasycalendar:calendar-detail',
                           kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})
        else:
            return super(DisplayConfigCreateView, self).get_success_url()


class DisplayUnitConfigCreateView(UserPassesTestMixin, generic.CreateView):
    model = DisplayUnitConfig
    form_class = DisplayUnitConfigCreateForm
    template_name = 'fantasycalendar/display_unit_config_create_form.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(DisplayUnitConfigCreateView, self).get_form()
        display_config = get_object_or_404(DisplayConfig, pk=self.kwargs['display_config_key'])
        form.fields['time_unit_page'].choices = \
            [(str(uc[0].pk) + ',' + (str(uc[1].pk) if uc[1] is not None else ''),
              'All ' + uc[1].time_unit_name + ' in a ' + uc[0].time_unit_name if uc[1] is not None else
              'Single ' + uc[0].time_unit_name)
             for uc in display_config.get_unused_display_unit_configs()]
        return form

    def form_valid(self, form):
        display_config = get_object_or_404(DisplayConfig, pk=self.kwargs['display_config_key'])
        form.instance.display_config = display_config

        time_unit_key = form.cleaned_data['time_unit_page'].split(',')[0]
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_key)
        form.instance.time_unit = time_unit

        sub_unit_key = form.cleaned_data['time_unit_page'].split(',')[1]
        if sub_unit_key:
            sub_unit = get_object_or_404(TimeUnit, pk=sub_unit_key)
            form.instance.sub_unit = sub_unit

        return super(DisplayUnitConfigCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.display_config.calendar.id,
                               'world_key': self.object.display_config.calendar.world.id})


class DateBookmarkCreateView(UserPassesTestMixin, generic.CreateView):
    model = DateBookmark
    form_class = DateBookmarkCreateForm
    template_name = 'fantasycalendar/date_bookmark_create_form.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_initial(self):
        initial = {}
        if 'bookmark_unit' in self.request.GET:
            initial['bookmark_unit'] = TimeUnit.objects.get(pk=int(self.request.GET['bookmark_unit']))
        if 'bookmark_iteration' in self.request.GET:
            initial['bookmark_iteration'] = int(self.request.GET['bookmark_iteration'])
        if 'bookmark_sub_unit' in self.request.GET:
            initial['bookmark_sub_unit'] = TimeUnit.objects.get(pk=int(self.request.GET['bookmark_sub_unit']))
        return initial

    def get_form(self, form_class=None):
        form = super(DateBookmarkCreateView, self).get_form()
        form.fields['bookmark_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        form.fields['bookmark_sub_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(DateBookmarkCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class WorldUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = World
    template_name = 'fantasycalendar/world_update_form.html'
    fields = ['world_name', 'public']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['pk'])
        return self.request.user == world.creator


class CalendarUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Calendar
    form_class = CalendarUpdateForm
    template_name = 'fantasycalendar/calendar_update_form.html'

    def test_func(self):
        world = get_object_or_404(Calendar, pk=self.kwargs['pk']).world
        return self.request.user == world.creator

    def form_valid(self, form):
        if form.instance.default_display_config:
            form.instance.default_display_config.default_display_unit_config = (
                form.cleaned_data)['default_time_unit_page']
            form.instance.default_display_config.default_date_bookmark = form.cleaned_data['default_date_bookmark']
            form.instance.default_display_config.save()
        return super(CalendarUpdateView, self).form_valid(form)


class TimeUnitUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_update_form.html'
    fields = ['time_unit_name', 'base_unit', 'length_cycle', 'base_unit_instance_names', 'default_date_format',
              'secondary_date_format']

    def test_func(self):
        world = get_object_or_404(TimeUnit, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(TimeUnitUpdateView, self).get_form()
        if TimeUnit.objects.get(pk=self.kwargs['pk']).is_bottom_level():
            form.fields['base_unit'].queryset = TimeUnit.objects.none()
        else:
            form.fields['base_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])\
                .exclude(pk=self.kwargs['pk'])
        form.fields['base_unit_instance_names'].label = \
            'Enter names of individual base units separated by spaces, if desired'
        form.fields['default_date_format'].queryset = DateFormat.objects.filter(time_unit_id=self.kwargs['pk'])
        form.fields['secondary_date_format'].queryset = DateFormat.objects.filter(time_unit_id=self.kwargs['pk'])
        return form

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class EventUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Event
    template_name = 'fantasycalendar/event_update_form.html'
    fields = ['event_name', 'event_description', 'bottom_level_iteration', 'display_order', 'event_group', 'visible']

    def test_func(self):
        world = get_object_or_404(Event, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(EventUpdateView, self).get_form()
        bottom_unit = Calendar.objects.get(pk=self.kwargs['calendar_key']).get_bottom_level_time_unit()
        form.fields['bottom_level_iteration'].label = \
            'Which ' + str(bottom_unit.time_unit_name) + ' does this event take place on?'

        class ModelChoiceFieldWithVisibility(forms.ModelChoiceField):
            def label_from_instance(self, obj):
                return obj.__str__() + ' (' + ('not ' if not obj.visible else '') + 'visible)'

        form.fields['event_group'] = ModelChoiceFieldWithVisibility(required=False,
            queryset=EventGroup.objects.filter(calendar_id=self.kwargs['calendar_key']))
        return form


class EventGroupUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = EventGroup
    template_name = 'fantasycalendar/event_group_update_form.html'
    fields = ['event_group_name', 'visible']

    def test_func(self):
        world = get_object_or_404(Event, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator


class DateFormatUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = DateFormat
    template_name = 'fantasycalendar/date_format_update_form.html'
    fields = ['date_format_name', 'format_string']

    def test_func(self):
        world = get_object_or_404(DateFormat, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        units_and_parents = []
        for unit in TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key']):
            units_and_parents.append((unit, unit.get_all_higher_containing_units()))
        context['units_and_parents'] = units_and_parents
        return context


class DisplayConfigUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = DisplayConfig
    form_class = DisplayConfigUpdateForm
    template_name = 'fantasycalendar/display_config_update_form.html'

    def test_func(self):
        world = get_object_or_404(DisplayConfig, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(DisplayConfigUpdateView, self).get_form()
        form.fields['default_display_unit_config'].queryset = DisplayUnitConfig.objects.filter(
            display_config_id=self.kwargs['pk'])
        form.fields['default_date_bookmark'].queryset = DateBookmark.objects.filter(
            calendar_id=self.kwargs['calendar_key'], personal_bookmark_creator=None)
        return form


class DisplayUnitConfigUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = DisplayUnitConfig
    form_class = DisplayUnitConfigUpdateForm
    template_name = 'fantasycalendar/display_unit_config_update_form.html'

    def test_func(self):
        world = get_object_or_404(DisplayUnitConfig, pk=self.kwargs['pk']).display_config.calendar.world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(DisplayUnitConfigUpdateView, self).get_form()
        form.fields['searchable_date_formats'].queryset = DateFormat.objects.filter(
            time_unit_id=form.instance.time_unit_id)
        form.fields['header_other_date_format'].queryset = DateFormat.objects.filter(
            time_unit_id=form.instance.time_unit_id)
        if form.instance.sub_unit:
            form.fields['sub_unit_other_date_format'].queryset = DateFormat.objects.filter(
                time_unit_id=form.instance.sub_unit_id)
            form.fields['row_grouping_time_unit'].queryset = TimeUnit.objects.filter(
                base_unit_id=form.instance.sub_unit_id)
            form.fields['block_grouping_time_unit'].queryset = TimeUnit.objects.filter(
                id__in=[unit.id for unit in form.instance.sub_unit.get_all_higher_containing_units()])
            form.fields['sub_unit_page'].queryset = DisplayUnitConfig.objects.filter(
                time_unit_id=form.instance.sub_unit_id, display_config_id=form.instance.display_config_id)
        elif form.instance.time_unit.base_unit:
            form.fields['sub_unit_other_date_format'].queryset = DateFormat.objects.filter(
                time_unit_id=form.instance.time_unit.base_unit_id)
            form.fields['row_grouping_time_unit'].queryset = TimeUnit.objects.filter(
                base_unit_id=form.instance.time_unit.base_unit_id)
            form.fields['block_grouping_time_unit'].queryset = TimeUnit.objects.filter(
                id__in=[unit.id for unit in form.instance.time_unit.base_unit.get_all_higher_containing_units()])
            form.fields['sub_unit_page'].queryset = DisplayUnitConfig.objects.filter(
                time_unit_id=form.instance.time_unit.base_unit_id, display_config_id=form.instance.display_config_id)
        else:
            form.fields['sub_unit_other_date_format'].queryset = DateFormat.objects.filter(
                time_unit_id=form.instance.time_unit_id)
            form.fields['row_grouping_time_unit'].queryset = TimeUnit.objects.filter(pk=form.instance.time_unit_id)
            form.fields['block_grouping_time_unit'].queryset = TimeUnit.objects.filter(pk=form.instance.time_unit_id)
            form.fields['sub_unit_page'].queryset = DisplayUnitConfig.objects.none()
        form.fields['row_unit_page'].queryset = DisplayUnitConfig.objects.filter(
            time_unit__in=form.fields['row_grouping_time_unit'].queryset,
            display_config_id=form.instance.display_config_id).exclude(id=form.instance.id)
        form.fields['block_unit_page'].queryset = DisplayUnitConfig.objects.filter(
            time_unit__in=form.fields['block_grouping_time_unit'].queryset,
            display_config_id=form.instance.display_config_id).exclude(id=form.instance.id)
        form.fields['linked_instance_display_name_type'].choices = \
            [x for x in form.fields['linked_instance_display_name_type'].choices
             if x[0] != DisplayUnitConfig.DisplayNameType.OTHER_FORMAT]
        return form

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.display_config.calendar.id,
                               'world_key': self.object.display_config.calendar.world.id})


class DateBookmarkUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = DateBookmark
    template_name = 'fantasycalendar/date_bookmark_update_form.html'
    fields = ['date_bookmark_name', 'bookmark_iteration']

    def test_func(self):
        world = get_object_or_404(DateBookmark, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class TimeUnitDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = TimeUnit
    template_name = 'fantasycalendar/time_unit_delete_form.html'

    def test_func(self):
        world = get_object_or_404(TimeUnit, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warnings = []
        for date_format in DateFormat.objects.filter(calendar_id=self.object.calendar.pk):
            if date_format.references_time_unit(self.object):
                warnings.append("Date format " + str(date_format) + " will also be deleted.")
        for display_unit_config in DisplayUnitConfig.objects.filter(
                Q(time_unit_id=self.object.pk) | Q(sub_unit_id=self.object.pk)):
            warnings.append("Time unit page " + str(display_unit_config) + " will also be deleted.")
        for display_unit_config in (DisplayUnitConfig.objects.exclude(time_unit_id=self.object.pk).
                exclude(sub_unit_id=self.object.pk).filter(row_grouping_time_unit_id=self.object.pk)):
            warnings.append("Time unit page " + str(display_unit_config) + " will have its row grouping removed.")
        for display_unit_config in (DisplayUnitConfig.objects.exclude(time_unit_id=self.object.pk).
                exclude(sub_unit_id=self.object.pk).filter(block_grouping_time_unit_id=self.object.pk)):
            warnings.append("Time unit page " + str(display_unit_config) + " will have its block grouping removed.")
        for date_bookmark in DateBookmark.objects.filter(
                Q(bookmark_unit_id=self.object.pk) | Q(bookmark_sub_unit_id=self.object.pk)):
            warnings.append("Date bookmark " + str(date_bookmark) + " will also be deleted.")
        context['warnings'] = warnings
        return context

    def form_valid(self, form):
        if self.object.is_bottom_level():
            raise IntegrityError  # do not allow deleting the bottom level time unit
        if not self.object.is_top_level():
            raise IntegrityError  # do not allow deleting time units that other time units are based on
        for date_format in DateFormat.objects.filter(calendar_id=self.object.calendar.pk):
            if date_format.references_time_unit(self.object):
                date_format.delete()  # CASCADE doesn't consider format strings so delete these manually
        return super(TimeUnitDeleteView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class EventDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Event
    template_name = 'fantasycalendar/event_delete_form.html'

    def test_func(self):
        world = get_object_or_404(Event, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warnings = []
        # no possible warnings right now but leaving this here for potential future use
        context['warnings'] = warnings
        return context

    def get_success_url(self):
        return reverse('fantasycalendar:time-unit-instance-detail',
                       kwargs={'world_key': self.object.calendar.world.id, 'calendar_key': self.object.calendar.id,
                               'pk': self.object.calendar.get_bottom_level_time_unit().id,
                               'iteration': self.object.bottom_level_iteration})


class EventGroupDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = EventGroup
    form_class = EventGroupDeleteForm
    template_name = 'fantasycalendar/event_group_delete_form.html'

    def test_func(self):
        world = get_object_or_404(EventGroup, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warnings = []
        # no possible warnings right now but leaving this here for potential future use
        context['warnings'] = warnings
        return context

    def form_valid(self, form):
        if form.cleaned_data['delete_events']:
            Event.objects.filter(event_group_id=self.object.id).delete()
        return super(EventGroupDeleteView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})


class DisplayUnitConfigDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = DisplayUnitConfig
    template_name = 'fantasycalendar/display_unit_config_delete_form.html'

    def test_func(self):
        world = get_object_or_404(DisplayUnitConfig, pk=self.kwargs['pk']).display_config.calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warnings = []
        if not self.object.time_unit.is_bottom_level() and not self.object.sub_unit:
            equivalent_page = 'All ' + str(self.object.time_unit.base_unit) + ' in a ' + str(self.object.time_unit)
            if any(self.object.time_unit == time_unit and self.object.time_unit.base_unit == base_unit
                   for time_unit, base_unit in self.object.display_config.get_unused_display_unit_configs()):
                page_extancy = 'can be created'
            else:
                page_extancy = 'already exists'
            warnings.append("Non-bottom-level pages with no sub unit can no longer be created, so if you delete this "
                            "page, you can't create it again. An equivalent page which " + page_extancy + " is \"" +
                            equivalent_page + "\".")
        context['warnings'] = warnings
        return context

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.display_config.calendar.id,
                               'world_key': self.object.display_config.calendar.world.id})


class DateBookmarkDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = DateBookmark
    template_name = 'fantasycalendar/date_bookmark_delete_form.html'

    def test_func(self):
        world = get_object_or_404(DateBookmark, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warnings = []
        if (self.object.calendar.default_display_config
                and self.object.calendar.default_display_config.default_date_bookmark
                and self.object.calendar.default_display_config.default_date_bookmark.pk == self.object.pk):
            warnings.append("This bookmark is set as the calendar default. Removing it will cause the calendar to "
                            "start on iteration 1 of its default page until a new bookmark is set.")
        context['warnings'] = warnings
        return context

    def get_success_url(self):
        return reverse('fantasycalendar:calendar-detail',
                       kwargs={'pk': self.object.calendar.id, 'world_key': self.object.calendar.world.id})
