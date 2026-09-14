from django.shortcuts import render

from main.models import Experience, Academic


def show_main(request):
    context = {
        "name": "Joel Sheldy Sucipto",
        "npm": "2506622494",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan software dan dunia bisnis."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Joel Sheldy Sucipto",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_academics(request):
    context = {
        "name": "Joel Sheldy Sucipto",
        "academic_list": Academic.objects.all(),
    }
    return render(request, "academics.html", context)