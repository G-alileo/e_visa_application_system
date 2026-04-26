from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.choices import UserRole
from apps.accounts.models import User
from apps.applications.choices import ApplicationStatus
from apps.applications.models import VisaApplication
from apps.visas.models import VisaType


class OfficerQueueFilterTests(TestCase):
    def setUp(self):
        self.officer = User.objects.create_user(
            email="officer@example.com",
            password="testpass123",
            role=UserRole.OFFICER,
        )
        self.applicant = User.objects.create_user(
            email="applicant@example.com",
            password="testpass123",
            role=UserRole.APPLICANT,
        )

        self.tourist_visa = VisaType.objects.create(
            code="TOURIST",
            name="Tourist Visa",
            description="",
            fee_amount=50,
            max_stay_days=30,
            is_active=True,
        )
        self.business_visa = VisaType.objects.create(
            code="BUSINESS",
            name="Business Visa",
            description="",
            fee_amount=120,
            max_stay_days=90,
            is_active=True,
        )
        self.inactive_visa = VisaType.objects.create(
            code="ARCHIVED",
            name="Archived Visa",
            description="",
            fee_amount=10,
            max_stay_days=15,
            is_active=False,
        )

        self._create_application(ApplicationStatus.UNDER_REVIEW, self.tourist_visa)
        self._create_application(ApplicationStatus.UNDER_REVIEW, self.business_visa)
        self._create_application(ApplicationStatus.PENDING_INFO, self.tourist_visa)
        self._create_application(ApplicationStatus.PENDING_INFO, self.business_visa)

        self.client.force_login(self.officer)

    def _create_application(self, status: str, visa_type: VisaType) -> VisaApplication:
        return VisaApplication.objects.create(
            applicant=self.applicant,
            visa_type=visa_type,
            status=status,
            nationality="NG",
            purpose_of_travel="Tourism",
            intended_entry_date=date.today() + timedelta(days=40),
            submitted_at=timezone.now(),
        )

    def test_filter_options_are_loaded_from_database(self):
        response = self.client.get(reverse("reviews:queue"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["visa_type_filters"],
            VisaType.objects.filter(is_active=True).order_by("name"),
            transform=lambda x: x,
        )
        self.assertNotContains(response, self.inactive_visa.name)

    def test_queue_can_be_filtered_by_selected_visa_type(self):
        response = self.client.get(
            reverse("reviews:queue"),
            {"visa_type": str(self.tourist_visa.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_visa_type_id"], str(self.tourist_visa.id))
        self.assertEqual(response.context["queue"].count(), 1)
        self.assertEqual(response.context["pending_info_queue"].count(), 1)
        self.assertEqual(response.context["queue"].first().visa_type_id, self.tourist_visa.id)
        self.assertEqual(response.context["pending_info_queue"].first().visa_type_id, self.tourist_visa.id)

    def test_invalid_visa_type_filter_is_ignored(self):
        response = self.client.get(reverse("reviews:queue"), {"visa_type": "999999"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_visa_type_id"], "")
        self.assertEqual(response.context["queue"].count(), 2)
        self.assertEqual(response.context["pending_info_queue"].count(), 2)
