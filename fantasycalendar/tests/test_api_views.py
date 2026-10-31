from django.urls import reverse
from rest_framework.test import APITestCase
from ..models import TimeUnit, Calendar, World, DateFormat, DisplayConfig, DisplayUnitConfig


class CalendarPageApiViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('fantasycalendar:calendar-page')

        cls.earth = World.objects.create(world_name='Earth', public=True)
        cls.julian = Calendar.objects.create(calendar_name='Julian Calendar', world=cls.earth)
        cls.day = TimeUnit.objects.create(time_unit_name='Day', calendar=cls.julian)
        cls.month = TimeUnit.objects.create(time_unit_name='Month', calendar=cls.julian, base_unit=cls.day,
                                            length_cycle='31 28.25 31 30 31 30 31 31 30 31 30 31')
        cls.year = TimeUnit.objects.create(time_unit_name='Year', calendar=cls.julian, base_unit=cls.month,
                                           length_cycle='12')

        cls.julian.ensure_default_display_config()
        cls.display_config = cls.julian.default_display_config
        cls.day_page = cls.display_config.default_display_unit_config
        cls.month_page = DisplayUnitConfig.objects.create(display_config=cls.display_config, time_unit=cls.month,
                                                          sub_unit=cls.day)
        cls.year_page = DisplayUnitConfig.objects.create(display_config=cls.display_config, time_unit=cls.year,
                                                         sub_unit=cls.month)
        cls.year_by_day_page = DisplayUnitConfig.objects.create(display_config=cls.display_config, time_unit=cls.year,
                                                                sub_unit=cls.day)

    def test_first_day_page_is_1_day(self):
        params = {'time_unit_id': self.day.pk, 'iteration': 1}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 1)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.day.pk)

    def test_first_month_by_day_page_is_31_days(self):
        params = {'time_unit_id': self.month.pk, 'sub_unit_id': self.day.pk, 'iteration': 1}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 31)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.day.pk)

    def test_second_month_by_day_page_is_28_days(self):
        params = {'time_unit_id': self.month.pk, 'sub_unit_id': self.day.pk, 'iteration': 2}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 28)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.day.pk)

    def test_first_year_by_month_page_is_12_months(self):
        params = {'time_unit_id': self.year.pk, 'sub_unit_id': self.month.pk, 'iteration': 1}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 12)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.month.pk)

    def test_first_year_by_day_page_is_365_days(self):
        params = {'time_unit_id': self.year.pk, 'sub_unit_id': self.day.pk, 'iteration': 1}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 365)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.day.pk)

    def test_fourth_year_by_day_page_is_366_days(self):
        params = {'time_unit_id': self.year.pk, 'sub_unit_id': self.day.pk, 'iteration': 4}

        response = self.client.get(self.url, query_params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['calendar_dates']), 366)
        self.assertEqual(response.data['calendar_dates'][0]['time_unit_id'], self.day.pk)
