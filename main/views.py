from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.models import Experience, Academic, Project
from main.forms import ProjectForm


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
    json_response = get_academics_json(request)
    academics = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    academics = [academic.object for academic in academics]

    context = {
        "name": "Joel Sheldy Sucipto",
        "academic_list": academics,
    }
    return render(request, "academics.html", context)

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Joel Sheldy Sucipto",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Joel Sheldy Sucipto",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def get_academics_json(request):
    academics = Academic.objects.all()
    academics_json = serializers.serialize("json", academics)
    return HttpResponse(academics_json, content_type="application/json")


def create_academic(request):
    form = AcademicForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat akademik berhasil ditambahkan!")
        return redirect("main:show_academics")

    context = {
        "name": "Joel Sheldy Sucipto",
        "form": form,
        "is_edit": False,
    }
    return render(request, "academics_form.html", context)


def update_academic(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)
    form = AcademicForm(request.POST or None, instance=academic)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat akademik berhasil diperbarui!")
        return redirect("main:show_academics")

    context = {
        "name": "Joel Sheldy Sucipto",
        "form": form,
        "is_edit": True,
        "academic": academic,
    }
    return render(request, "academics_form.html", context)


def delete_academic(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)

    if request.method == "POST":
        academic.delete()
        messages.success(request, "Riwayat akademik berhasil dihapus!")
        return redirect("main:show_academics")

    return redirect("main:show_academics")