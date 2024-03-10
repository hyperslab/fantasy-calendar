from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark, DisplayUnitConfig
from .forms import DisplayConfigCreateForm, DisplayConfigUpdateForm, DisplayUnitConfigUpdateForm


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
        if 'display_unit_type' in self.request.GET:
            context['display_unit'] = TimeUnit.objects.get(pk=self.request.GET['display_unit_type'])
        elif self.object.default_display_config:
            context['display_unit'] = self.object.default_display_config.display_unit
        else:
            self.object.ensure_bottom_level_time_unit()  # if unit not specified, it might not have one yet
            context['display_unit'] = TimeUnit.objects.filter(calendar_id=self.object.id).first()
        if 'nest_checkbox' in self.request.GET:
            context['nest_level'] = int(self.request.GET['nest_checkbox'])
        elif self.object.default_display_config:
            context['nest_level'] = self.object.default_display_config.nest_level
        else:
            context['nest_level'] = 0
        if 'iteration' in self.request.GET:
            context['iteration'] = int(self.request.GET['iteration'])
        elif self.object.default_display_config and self.object.default_display_config.default_date_bookmark:
            context['iteration'] = self.object.default_display_config.default_date_bookmark.bookmark_iteration
        else:
            context['iteration'] = 1

        context['instance_display_name'] = context['display_unit'].get_instance_display_name(context['iteration'])

        if context['nest_level'] > 0 and context['display_unit'].base_unit is not None and \
                context['display_unit'].base_unit.base_unit is not None:
            context['display_nested'] = True
            display_instances = context['display_unit'].get_base_unit_instances(iteration=context['iteration'])
            display_base_names = []
            nested_custom_names = context['display_unit'].base_unit.get_base_unit_instance_names()
            first_middle_instance_iteration = context['display_unit'].\
                get_first_base_unit_instance_iteration_at_iteration(iteration=context['iteration'])
            first_base_instance_iteration = context['display_unit'].base_unit.\
                get_first_base_unit_instance_iteration_at_iteration(iteration=first_middle_instance_iteration)
            for name, length in display_instances:
                nested_display_base_names = []
                for i in range(length):
                    if i < len(nested_custom_names):
                        nested_display_base_name = nested_custom_names[i]
                    else:
                        nested_display_base_name = str(context['display_unit'].base_unit.base_unit.time_unit_name) + \
                                                   ' ' + str(i + 1)
                    iteration = first_base_instance_iteration + i
                    events = context['display_unit'].base_unit.base_unit.get_events_at_iteration(iteration=iteration)
                    nested_display_base_names.append((nested_display_base_name, iteration, events))
                display_base_names.append((name, first_middle_instance_iteration, nested_display_base_names))
                first_middle_instance_iteration += 1
                first_base_instance_iteration += length
            context['display_base_names'] = display_base_names
            context['smallest_display_unit'] = context['display_unit'].base_unit.base_unit
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
                    iteration = first_base_instance_iteration + (i - 1)
                    events = context['display_unit'].base_unit.get_events_at_iteration(iteration=iteration)
                    display_base_names.append((display_base_name, iteration, events))
                context['smallest_display_unit'] = context['display_unit'].base_unit
            else:
                events = context['display_unit'].get_events_at_iteration(iteration=context['iteration'])
                display_base_names.append((context['display_unit'].time_unit_name + ' 1', context['iteration'], events))
                context['smallest_display_unit'] = context['display_unit']
            context['display_base_names'] = display_base_names

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
        return context


class EventDetailView(UserPassesTestMixin, generic.DetailView):
    model = Event
    template_name = 'fantasycalendar/event_detail.html'

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return world.public or self.request.user == world.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.calendar.get_bottom_level_time_unit().default_date_format:
            context['display_date'] = self.object.calendar.get_bottom_level_time_unit().default_date_format.\
                get_formatted_date(self.object.bottom_level_iteration)
        else:
            context['display_date'] = str(self.object.calendar.get_bottom_level_time_unit().time_unit_name) + ' ' + \
                                      str(self.object.bottom_level_iteration)
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
        possible_time_units = TimeUnit.objects.filter(calendar_id=self.object.calendar_id)
        existing_unit_configs = self.object.displayunitconfig_set.all()
        context['can_add_unit_configs'] = True if len(possible_time_units) > len(existing_unit_configs) else False
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
    fields = ['calendar_name']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def form_valid(self, form):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        form.instance.world = world
        form.instance.save()
        form.instance.ensure_bottom_level_time_unit()
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
    fields = ['event_name', 'event_description', 'bottom_level_iteration']

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
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        return super(EventCreateView, self).form_valid(form)

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
        form.fields['display_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        form.fields['default_date_bookmark'].queryset = DateBookmark.objects.filter(
            calendar_id=self.kwargs['calendar_key'])
        return form

    def form_valid(self, form):
        calendar = get_object_or_404(Calendar, pk=self.kwargs['calendar_key'])
        form.instance.calendar = calendar
        form.instance.save()
        time_units = calendar.timeunit_set.all()
        for time_unit in time_units:
            DisplayUnitConfig.objects.create(display_config=form.instance, time_unit=time_unit)
        return super(DisplayConfigCreateView, self).form_valid(form)


class DisplayUnitConfigCreateView(UserPassesTestMixin, generic.CreateView):
    model = DisplayUnitConfig
    template_name = 'fantasycalendar/display_unit_config_create_form.html'
    fields = ['time_unit']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(DisplayUnitConfigCreateView, self).get_form()
        form.fields['time_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        display_config = get_object_or_404(DisplayConfig, pk=self.kwargs['display_config_key'])
        if display_config.displayunitconfig_set:  # exclude time units that already have configs for this display config
            for display_unit_config in display_config.displayunitconfig_set.all():
                form.fields['time_unit'].queryset = form.fields['time_unit'].queryset.exclude(
                    pk=display_unit_config.time_unit_id)
        return form

    def form_valid(self, form):
        display_config = get_object_or_404(DisplayConfig, pk=self.kwargs['display_config_key'])
        form.instance.display_config = display_config
        return super(DisplayUnitConfigCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fantasycalendar:display-config-detail',
                       kwargs={'pk': self.object.display_config.id,
                               'world_key': self.object.display_config.calendar.world.id,
                               'calendar_key': self.object.display_config.calendar.id})


class DateBookmarkCreateView(UserPassesTestMixin, generic.CreateView):
    model = DateBookmark
    template_name = 'fantasycalendar/date_bookmark_create_form.html'
    fields = ['date_bookmark_name', 'bookmark_unit', 'bookmark_iteration']

    def test_func(self):
        world = get_object_or_404(World, pk=self.kwargs['world_key'])
        return self.request.user == world.creator

    def get_initial(self):
        initial = {}
        if 'bookmark_unit' in self.request.GET:
            initial['bookmark_unit'] = TimeUnit.objects.get(pk=int(self.request.GET['bookmark_unit']))
        if 'bookmark_iteration' in self.request.GET:
            initial['bookmark_iteration'] = int(self.request.GET['bookmark_iteration'])
        return initial

    def get_form(self, form_class=None):
        form = super(DateBookmarkCreateView, self).get_form()
        form.fields['bookmark_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
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
    template_name = 'fantasycalendar/calendar_update_form.html'
    fields = ['calendar_name', 'default_display_config']

    def test_func(self):
        world = get_object_or_404(Calendar, pk=self.kwargs['pk']).world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(CalendarUpdateView, self).get_form()
        form.fields['default_display_config'].queryset = DisplayConfig.objects.filter(calendar_id=self.kwargs['pk'])
        return form


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
    fields = ['event_name', 'event_description', 'bottom_level_iteration']

    def test_func(self):
        world = get_object_or_404(Event, pk=self.kwargs['pk']).calendar.world
        return self.request.user == world.creator

    def get_form(self, form_class=None):
        form = super(EventUpdateView, self).get_form()
        bottom_unit = Calendar.objects.get(pk=self.kwargs['calendar_key']).get_bottom_level_time_unit()
        form.fields['bottom_level_iteration'].label = \
            'Which ' + str(bottom_unit.time_unit_name) + ' does this event take place on?'
        return form


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
        form.fields['display_unit'].queryset = TimeUnit.objects.filter(calendar_id=self.kwargs['calendar_key'])
        form.fields['default_date_bookmark'].queryset = DateBookmark.objects.filter(
            calendar_id=self.kwargs['calendar_key'])
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
        if form.instance.time_unit.base_unit:
            form.fields['base_unit_other_date_format'].queryset = DateFormat.objects.filter(
                time_unit_id=form.instance.time_unit.base_unit_id)
        else:
            form.fields['base_unit_other_date_format'].queryset = DateFormat.objects.filter(
                time_unit_id=form.instance.time_unit_id)
        if form.instance.time_unit.base_unit:
            form.fields['row_grouping_time_unit'].queryset = TimeUnit.objects.filter(
                base_unit_id=form.instance.time_unit.base_unit.id)
        else:
            form.fields['row_grouping_time_unit'].queryset = TimeUnit.objects.filter(pk=form.instance.time_unit.id)
        return form

    def get_success_url(self):
        return reverse('fantasycalendar:display-config-detail',
                       kwargs={'pk': self.object.display_config.id,
                               'world_key': self.object.display_config.calendar.world.id,
                               'calendar_key': self.object.display_config.calendar.id})


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
