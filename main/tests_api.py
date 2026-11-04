import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class ProjectApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password"
        )
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password"
        )
        self.project = Project.objects.create(
            title="Portfolio",
            description="A portfolio website.",
            tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse(
            "api:project-detail", kwargs={"project_id": self.project.pk}
        )

    def project_payload(self, **overrides):
        payload = {
            "title": "New project",
            "description": "A project description.",
            "tech_stack": "Django, Python",
            "project_url": "https://example.com/project",
            "project_image_url": "",
        }
        payload.update(overrides)
        return payload

    def test_guest_can_list_projects(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["title"], "Portfolio")
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertFalse(response.data[0]["is_starred"])
        head_response = self.client.head(self.list_url)
        self.assertEqual(head_response.status_code, 200)
        self.assertEqual(head_response.content, b"")

    def test_list_filters_by_title(self):
        Project.objects.create(
            title="Alpha work", description="Description", tech_stack="Python"
        )
        Project.objects.create(
            title="Other work", description="Description", tech_stack="Python"
        )

        all_projects = self.client.get(self.list_url)
        self.assertEqual(
            [project["title"] for project in all_projects.data],
            ["Alpha work", "Other work", "Portfolio"],
        )

        response = self.client.get(self.list_url, {"title": "portfolio"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Portfolio")
        empty_response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(empty_response.status_code, 200)
        self.assertEqual(empty_response.data, [])

    def test_guest_can_read_project_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.project.pk))
        self.assertEqual(self.client.head(self.detail_url).status_code, 200)
        missing_url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing_url).status_code, 404)

    def test_owner_can_create_project_and_html_is_stripped(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            self.project_payload(
                title="<b>New project</b>",
                star_count=99,
                is_starred=True,
                starred_by_names="forged",
                starred_by=[self.visitor.pk],
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New project")
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_owner_cannot_create_project_with_blank_title(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url, self.project_payload(title="  "), format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)
        xss_response = self.client.post(
            self.list_url,
            self.project_payload(title='<img src="x" onerror="alert(1)">'),
            format="json",
        )
        self.assertEqual(xss_response.status_code, 400)
        self.assertIn("title", xss_response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_owner_cannot_create_project_with_javascript_url(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.list_url,
            self.project_payload(project_url="javascript:alert(1)"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("project_url", response.data)

    def test_guest_cannot_create_project(self):
        response = self.client.post(
            self.list_url, self.project_payload(), format="json"
        )

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_create_project(self):
        self.client.force_authenticate(self.visitor)

        response = self.client.post(
            self.list_url, self.project_payload(), format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.visitor.is_staff = True
        self.visitor.save()
        staff_response = self.client.post(
            self.list_url, self.project_payload(), format="json"
        )
        self.assertEqual(staff_response.status_code, 403)
        self.visitor.is_staff = False
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        editor_response = self.client.post(
            self.list_url, self.project_payload(), format="json"
        )
        self.assertEqual(editor_response.status_code, 403)

    def test_owner_can_patch_project(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            self.detail_url, {"title": "Updated portfolio"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated portfolio")
        self.assertEqual(response.data["description"], "A portfolio website.")
        incomplete_put = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json"
        )
        self.assertEqual(incomplete_put.status_code, 400)
        complete_put = self.client.put(
            self.detail_url, self.project_payload(title="Replacement"), format="json"
        )
        self.assertEqual(complete_put.status_code, 200)
        self.assertEqual(complete_put.data["title"], "Replacement")

    def test_regular_user_cannot_patch_project(self):
        self.client.force_authenticate(self.visitor)

        response = self.client.patch(
            self.detail_url, {"title": "Not allowed"}, format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        editor_response = self.client.patch(
            self.detail_url, {"title": "Not allowed"}, format="json"
        )
        self.assertEqual(editor_response.status_code, 403)
        self.visitor.is_staff = True
        self.visitor.save()
        staff_response = self.client.patch(
            self.detail_url, {"title": "Not allowed"}, format="json"
        )
        self.assertEqual(staff_response.status_code, 403)

    def test_owner_can_delete_project(self):
        self.client.force_authenticate(self.owner)

        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_regular_user_cannot_delete_project(self):
        self.client.force_authenticate(self.visitor)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        editor_response = self.client.delete(self.detail_url)
        self.assertEqual(editor_response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_requires_login_and_authenticated_user_can_toggle(self):
        star_url = reverse(
            "api:project-star", kwargs={"project_id": self.project.pk}
        )
        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get(star_url).status_code, 403)

        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.get(star_url).status_code, 405)
        response = self.client.post(star_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["id"], str(self.project.pk))
        self.assertIn("starred_by_names", response.data)
        self.assertEqual(
            Project.objects.get(pk=self.project.pk).starred_by.get().username,
            "visitor",
        )

        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

        csrf_client = APIClient(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        rejected = csrf_client.post(self.list_url, self.project_payload(), format="json")
        self.assertEqual(rejected.status_code, 403)
        page = csrf_client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, 200)
        csrf_token = csrf_client.cookies["csrftoken"].value
        accepted = csrf_client.post(
            self.list_url,
            self.project_payload(),
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(accepted.status_code, 201)
