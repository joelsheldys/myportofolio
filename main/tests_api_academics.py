import json
import uuid

from django.contrib.auth.models import Group, User
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Academic


class AcademicApiBase(APITestCase):
    password = "test-password"

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password=self.password,
        )
        self.editor = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password=self.password,
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.visitor = User.objects.create_user(
            username="visitor",
            email="visitor@example.com",
            password=self.password,
        )
        self.other_group_user = User.objects.create_user(
            username="other-group",
            email="other@example.com",
            password=self.password,
        )
        self.other_group_user.groups.add(Group.objects.create(name="Other"))
        self.academic = Academic.objects.create(
            institution="Institut Teladan",
            level="kuliah",
            start_year=2020,
            end_year=2024,
        )
        self.list_url = reverse("api:academic-list")
        self.detail_url = reverse(
            "api:academic-detail", kwargs={"academic_id": self.academic.pk}
        )
        self.star_url = reverse(
            "api:academic-star", kwargs={"academic_id": self.academic.pk}
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

    def academic_snapshot(self):
        academics = list(
            Academic.objects.order_by("pk").values_list(
                "pk", "institution", "level", "start_year", "end_year"
            )
        )
        stars = list(
            Academic._meta.get_field("starred_by")
            .remote_field.through.objects.order_by("academic_id", "user_id")
            .values_list("academic_id", "user_id")
        )
        return academics, stars

    def assert_rejected_without_changes(self, request, status_code=403):
        before = self.academic_snapshot()
        response = request()
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(self.academic_snapshot(), before)
        return response


class AcademicApiTests(AcademicApiBase):
    def test_guest_can_list_detail_and_head_academics(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["institution"], "Institut Teladan")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(self.client.head(self.list_url).status_code, 200)

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data["period"], "2020 - 2024")
        head_response = self.client.head(self.detail_url)
        self.assertEqual(head_response.status_code, 200)
        self.assertEqual(head_response.content, b"")

    def test_missing_academic_returns_404(self):
        missing_url = reverse("api:academic-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing_url).status_code, 404)

    def test_search_is_case_insensitive_and_ignores_surrounding_spaces(self):
        Academic.objects.create(
            institution="Sekolah Lain", level="sma", start_year=2017
        )

        response = self.client.get(self.list_url, {"q": "  tElAdAn  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["institution"], "Institut Teladan")

        all_response = self.client.get(self.list_url, {"q": "   "})
        self.assertEqual(len(all_response.data), 2)

    def test_academics_are_ordered_by_start_year_institution_and_id(self):
        Academic.objects.create(institution="Zeta", level="sma", start_year=2017)
        Academic.objects.create(institution="Alpha", level="sma", start_year=2017)

        response = self.client.get(self.list_url)
        self.assertEqual(
            [item["institution"] for item in response.data],
            ["Alpha", "Zeta", "Institut Teladan"],
        )

    def test_response_does_not_expose_account_data(self):
        self.academic.starred_by.add(self.visitor)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        serialized = json.dumps(response.data)
        self.assertNotIn("username", serialized)
        self.assertNotIn("email", serialized)
        self.assertNotIn("password", serialized)
        self.assertNotIn("visitor", serialized)
        self.assertNotIn("starred_by", response.data[0])

    def test_is_starred_is_specific_to_authenticated_request_user(self):
        self.academic.starred_by.add(self.visitor)

        self.client.force_authenticate(self.visitor)
        visitor_response = self.client.get(self.list_url)
        self.assertTrue(visitor_response.data[0]["is_starred"])

        self.client.force_authenticate(self.editor)
        editor_response = self.client.get(self.list_url)
        self.assertFalse(editor_response.data[0]["is_starred"])

    def test_browsable_api_is_available_for_list_and_detail(self):
        list_response = self.client.get(self.list_url, HTTP_ACCEPT="text/html")
        detail_response = self.client.get(self.detail_url, HTTP_ACCEPT="text/html")

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Institut Teladan")
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Institut Teladan")

    def test_guest_cannot_write_and_database_is_unchanged(self):
        requests = (
            lambda: self.client.post(
                self.list_url, self.academic_payload(), format="json"
            ),
            lambda: self.client.put(
                self.detail_url, self.academic_payload(), format="json"
            ),
            lambda: self.client.patch(
                self.detail_url, {"institution": "Rejected"}, format="json"
            ),
            lambda: self.client.delete(self.detail_url),
        )
        for request in requests:
            with self.subTest(request=request):
                self.assert_rejected_without_changes(request)

    def test_regular_users_cannot_write_and_database_is_unchanged(self):
        for user in (self.visitor, self.other_group_user):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                requests = (
                    lambda: self.client.post(
                        self.list_url, self.academic_payload(), format="json"
                    ),
                    lambda: self.client.put(
                        self.detail_url, self.academic_payload(), format="json"
                    ),
                    lambda: self.client.patch(
                        self.detail_url, {"institution": "Rejected"}, format="json"
                    ),
                    lambda: self.client.delete(self.detail_url),
                )
                for request in requests:
                    self.assert_rejected_without_changes(request)

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(self.editor)
        patch_response = self.client.patch(
            self.detail_url, {"institution": "Edited by editor"}, format="json"
        )
        self.assertEqual(patch_response.status_code, 200)
        self.academic.refresh_from_db()
        self.assertEqual(self.academic.institution, "Edited by editor")

        put_response = self.client.put(
            self.detail_url,
            self.academic_payload(institution="Replaced by editor"),
            format="json",
        )
        self.assertEqual(put_response.status_code, 200)
        self.academic.refresh_from_db()
        self.assertEqual(self.academic.institution, "Replaced by editor")

        self.assert_rejected_without_changes(
            lambda: self.client.post(
                self.list_url, self.academic_payload(), format="json"
            )
        )
        self.assert_rejected_without_changes(lambda: self.client.delete(self.detail_url))

    def test_owner_can_create_patch_put_and_delete(self):
        self.client.force_authenticate(self.owner)

        create_response = self.client.post(
            self.list_url, self.academic_payload(), format="json"
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertTrue(Academic.objects.filter(pk=create_response.data["id"]).exists())

        patch_response = self.client.patch(
            self.detail_url, {"institution": "Patched by owner"}, format="json"
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data["institution"], "Patched by owner")

        put_response = self.client.put(
            self.detail_url,
            self.academic_payload(institution="Replaced by owner"),
            format="json",
        )
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.data["institution"], "Replaced by owner")

        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Academic.objects.filter(pk=self.academic.pk).exists())

    def test_html_only_institution_is_rejected_without_database_change(self):
        self.client.force_authenticate(self.owner)
        for institution in ("", "   ", "<b></b>"):
            with self.subTest(institution=institution):
                self.assert_rejected_without_changes(
                    lambda: self.client.patch(
                        self.detail_url, {"institution": institution}, format="json"
                    ),
                    status_code=400,
                )

    def test_unknown_level_is_rejected_without_database_change(self):
        self.client.force_authenticate(self.owner)
        self.assert_rejected_without_changes(
            lambda: self.client.patch(
                self.detail_url, {"level": "unknown"}, format="json"
            ),
            status_code=400,
        )

    def test_post_and_put_require_mandatory_fields_without_database_change(self):
        self.client.force_authenticate(self.owner)
        self.assert_rejected_without_changes(
            lambda: self.client.post(
                self.list_url, {"institution": "Missing fields"}, format="json"
            ),
            status_code=400,
        )
        self.assert_rejected_without_changes(
            lambda: self.client.put(
                self.detail_url, {"institution": "Missing fields"}, format="json"
            ),
            status_code=400,
        )

    def test_year_boundaries_and_out_of_range_years(self):
        self.client.force_authenticate(self.owner)
        for year in (1899, 2101):
            with self.subTest(year=year):
                self.assert_rejected_without_changes(
                    lambda: self.client.patch(
                        self.detail_url, {"start_year": year}, format="json"
                    ),
                    status_code=400,
                )

        response = self.client.post(
            self.list_url,
            self.academic_payload(start_year=1900, end_year=2100),
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_end_year_before_start_is_rejected_for_create_and_patch(self):
        self.client.force_authenticate(self.owner)
        self.assert_rejected_without_changes(
            lambda: self.client.post(
                self.list_url,
                self.academic_payload(start_year=2025, end_year=2024),
                format="json",
            ),
            status_code=400,
        )
        self.assert_rejected_without_changes(
            lambda: self.client.patch(
                self.detail_url, {"end_year": 2019}, format="json"
            ),
            status_code=400,
        )

    def test_null_end_year_clears_end_year(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.detail_url, {"end_year": None}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["end_year"])
        self.academic.refresh_from_db()
        self.assertIsNone(self.academic.end_year)

    def test_read_only_fields_are_ignored(self):
        self.client.force_authenticate(self.owner)
        forged_id = uuid.uuid4()
        response = self.client.post(
            self.list_url,
            self.academic_payload(
                id=str(forged_id),
                period="forged",
                star_count=999,
                is_starred=True,
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], str(forged_id))
        self.assertEqual(response.data["period"], "2022 - 2025")
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_strips_html_from_institution(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            self.list_url,
            self.academic_payload(institution="<b>Universitas Contoh</b>"),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["institution"], "Universitas Contoh")

    def test_guest_cannot_star_without_database_change(self):
        self.assert_rejected_without_changes(
            lambda: self.client.post(self.star_url), status_code=403
        )

    def test_star_toggles_for_request_user_and_ignores_body_user(self):
        self.client.force_authenticate(self.visitor)
        first_response = self.client.post(
            self.star_url, {"user_id": self.owner.pk}, format="json"
        )
        self.assertEqual(first_response.status_code, 200)
        self.assertTrue(first_response.data["is_starred"])
        self.assertEqual(first_response.data["star_count"], 1)
        self.assertEqual(
            list(self.academic.starred_by.values_list("pk", flat=True)),
            [self.visitor.pk],
        )

        second_response = self.client.post(self.star_url)
        self.assertEqual(second_response.status_code, 200)
        self.assertFalse(second_response.data["is_starred"])
        self.assertEqual(second_response.data["star_count"], 0)

    def test_star_counts_users_and_is_allowed_for_editor_and_owner(self):
        for user in (self.editor, self.owner, self.visitor):
            self.client.force_authenticate(user)
            response = self.client.post(self.star_url)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["star_count"], 3)
        self.assertEqual(self.academic.starred_by.count(), 3)

    def test_star_not_found_and_method_handling(self):
        missing_star_url = reverse("api:academic-star", args=[uuid.uuid4()])
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.post(missing_star_url).status_code, 404)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.assertEqual(self.client.delete(self.star_url).status_code, 405)

    def test_guest_get_star_returns_forbidden(self):
        self.assertEqual(self.client.get(self.star_url).status_code, 403)


class AcademicCsrfTests(AcademicApiBase):
    def logged_in_client(self, username):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=username, password=self.password))
        return client

    def test_patch_without_csrf_token_is_rejected_without_database_change(self):
        client = self.logged_in_client("editor")
        before = self.academic_snapshot()
        response = client.patch(
            self.detail_url, {"institution": "No token"}, format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.academic_snapshot(), before)

    def test_page_cookie_token_allows_patch_and_get_needs_no_token(self):
        client = self.logged_in_client("editor")
        page_response = client.get(reverse("main:show_academics"))
        csrf_token = page_response.cookies["csrftoken"].value

        self.assertEqual(client.get(self.detail_url).status_code, 200)
        patch_response = client.patch(
            self.detail_url,
            {"institution": "Updated with CSRF"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(patch_response.status_code, 200)
        self.academic.refresh_from_db()
        self.assertEqual(self.academic.institution, "Updated with CSRF")

    def test_owner_post_and_delete_without_token_are_rejected(self):
        client = self.logged_in_client("owner")
        self.assert_rejected_without_changes(
            lambda: client.post(
                self.list_url, self.academic_payload(), format="json"
            )
        )
        self.assert_rejected_without_changes(lambda: client.delete(self.detail_url))

    def test_regular_user_can_star_with_csrf_token(self):
        client = self.logged_in_client("visitor")
        page_response = client.get(reverse("main:show_academics"))
        csrf_token = page_response.cookies["csrftoken"].value

        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=csrf_token)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_starred"])


class AcademicPageTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", email="owner@example.com", password="test-password"
        )
        self.editor = User.objects.create_user(
            username="editor", email="editor@example.com", password="test-password"
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="test-password"
        )
        self.url = reverse("main:show_academics")

    def assert_page_role(self, user=None, can_manage=False, can_edit=False):
        client = Client()
        if user is not None:
            client.force_login(user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)
        self.assertContains(
            response,
            f'data-can-manage="{"true" if can_manage else "false"}"',
        )
        self.assertContains(
            response, f'data-can-edit="{"true" if can_edit else "false"}"'
        )
        self.assertContains(
            response, f'data-list-url="{reverse("api:academic-list")}"'
        )
        self.assertContains(response, 'src="/static/js/utils.js"')
        self.assertContains(response, 'src="/static/js/academics.js"')

        if can_manage:
            self.assertContains(response, 'id="academic-add-button"')
            self.assertContains(response, 'id="academic-delete-modal"')
        else:
            self.assertNotContains(response, 'id="academic-add-button"')
            self.assertNotContains(response, 'id="academic-delete-modal"')

        if can_edit:
            self.assertContains(response, 'id="academic-form-modal"')
        else:
            self.assertNotContains(response, 'id="academic-form-modal"')

    def test_csrf_cookie_and_controls_match_each_role(self):
        self.assert_page_role()
        self.assert_page_role(self.user)
        self.assert_page_role(self.editor, can_edit=True)
        self.assert_page_role(self.owner, can_manage=True, can_edit=True)
