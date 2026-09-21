from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput

from main.models import Project, Academic

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/joelsheldys/myportofolio",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class AcademicForm(ModelForm):
    class Meta:
        model = Academic
        fields = [
            "institution",
            "level",
            "start_year",
            "end_year",
        ]

        labels = {
            "institution": "Nama Institusi",
            "level": "Jenjang Pendidikan",
            "start_year": "Tahun Mulai",
            "end_year": "Tahun Selesai",
        }

        widgets = {
            "institution": TextInput(
                attrs={"placeholder": "Universitas Indonesia"}
            ),
            "start_year": NumberInput(attrs={"placeholder": "2022"}),
            "end_year": NumberInput(
                attrs={"placeholder": "Kosongkan jika masih berlangsung"}
            ),
        }