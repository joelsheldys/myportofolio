from django.contrib.auth.models import Group, User
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase

from main.models import Academic


class AcademicApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password"
        )
        self.editor = User.objects.create_user(
            username="editor", password="test-password"
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password"
        )
        self.academic = Academic.objects.create(
            institution="Institut Teladan",
            level="kuliah",
            start_year=2020,
        )
        self.list_url = reverse("api:academic-list")
        self.detail_url = reverse(
            "api:academic-detail", kwargs={"academic_id": self.academic.pk}
        )

    def academic_payload(self, **overrides):
        payload = {
            "institution": "Universitas Contoh",
            "level": "kuliah",
            "start_year": 2022,
            "end_year": 2025,
        }
        payload.update(overrides)
        return payload

    def test_guest_can_read_academics_without_star_account_names(self):
        self.academic.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)
        legacy_response = self.client.get(reverse("main:get_academics_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["institution"], "Institut Teladan")
        self.assertNotIn("starred_by_names", response.data[0])
        self.assertEqual(legacy_response.status_code, 200)
        self.assertNotIn("visitor", legacy_response.content.decode())

    def test_academics_search_filters_institution(self):
        Academic.objects.create(
            institution="Sekolah Lain", level="sma", start_year=2017
        )

        response = self.client.get(self.list_url, {"q": "teladan"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["institution"], "Institut Teladan")

    def test_guest_can_read_academic_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["period"], "2020 - Sekarang")
        self.assertEqual(response.data["level_display"], "Perguruan Tinggi")

    def test_owner_can_create_academic(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url, self.academic_payload(), format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["institution"], "Universitas Contoh")

    def test_editor_cannot_create_academic(self):
        self.client.force_authenticate(self.editor)

        response = self.client.post(
            self.list_url, self.academic_payload(), format="json"
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_patch_academic(self):
        self.client.force_authenticate(self.editor)

        response = self.client.patch(
            self.detail_url, {"institution": "Updated institution"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["institution"], "Updated institution")

    def test_editor_can_put_academic(self):
        self.client.force_authenticate(self.editor)

        response = self.client.put(
            self.detail_url,
            self.academic_payload(institution="Replaced institution"),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["institution"], "Replaced institution")

    def test_editor_cannot_delete_academic(self):
        self.client.force_authenticate(self.editor)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Academic.objects.filter(pk=self.academic.pk).exists())

    def test_owner_can_patch_academic(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            self.detail_url, {"end_year": 2024}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["period"], "2020 - 2024")

    def test_owner_can_delete_academic(self):
        self.client.force_authenticate(self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Academic.objects.filter(pk=self.academic.pk).exists())

    def test_rejects_end_year_before_start_year_on_create(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            self.academic_payload(start_year=2025, end_year=2024),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("end_year", response.data)

    def test_rejects_end_year_before_start_year_on_partial_update(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            self.detail_url, {"end_year": 2019}, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("end_year", response.data)

    def test_strips_html_from_institution(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            self.academic_payload(institution="<b>Universitas Contoh</b>"),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["institution"], "Universitas Contoh")

    def test_authenticated_user_can_toggle_academic_star(self):
        star_url = reverse(
            "api:academic-star", kwargs={"academic_id": self.academic.pk}
        )
        self.client.force_authenticate(self.visitor)

        response = self.client.post(star_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

    def test_project_page_sets_csrf_cookie_for_regular_user_and_api_checks_it(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.editor)

        page_response = client.get(reverse("main:show_projects"))
        csrf_token = page_response.cookies["csrftoken"].value
        response_without_token = client.patch(
            self.detail_url, {"institution": "Updated"}, content_type="application/json"
        )

        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'data-is-superuser="false"')
        self.assertContains(page_response, 'data-is-authenticated="true"')
        self.assertEqual(response_without_token.status_code, 403)

        api_response = client.patch(
            self.detail_url,
            b'{"institution":"Updated"}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json()["institution"], "Updated")
