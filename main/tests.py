from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Academic


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class AcademicsTest(TestCase):
    def setUp(self):
        self.academic = Academic.objects.create(
            institution="Universitas Indonesia",
            level="kuliah",
            start_year=2025,
        )

    def test_academics_url_is_accessible(self):
        response = self.client.get(reverse("main:show_academics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "academics.html")

    def test_academics_page_shows_data(self):
        response = self.client.get(reverse("main:show_academics"))
        self.assertContains(response, self.academic.institution)
        self.assertContains(response, "Perguruan Tinggi")
        self.assertContains(response, "2025 - Sekarang")

    def test_empty_academics_page(self):
        Academic.objects.all().delete()
        response = self.client.get(reverse("main:show_academics"))
        self.assertContains(response, "Belum ada riwayat akademik yang ditambahkan.")

    def test_academic_model(self):
        self.assertEqual(str(self.academic), "Universitas Indonesia")
        self.assertTrue(self.academic.is_ongoing)

    def test_completed_academic_period(self):
        self.academic.end_year = 2029
        self.academic.save()
        self.assertFalse(self.academic.is_ongoing)
        self.assertEqual(self.academic.period, "2025 - 2029")

    def test_navbar_has_academics_link(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, f'href="{reverse("main:show_academics")}"')