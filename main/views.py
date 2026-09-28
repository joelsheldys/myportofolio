import datetime

from django.contrib import messages
from django.core import serializers
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from main.models import Experience, Academic, Project
from main.forms import ProjectForm, AcademicForm
from main.permissions import can_edit, can_manage, role_required
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied   

OWNER_NAME = "Joel Sheldy Sucipto"
ACADEMIC_JSON_FIELDS = ("institution", "level", "start_year", "end_year")
PROJECT_JSON_FIELDS = ("title", "description", "tech_stack", "project_url", "project_image_url")


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": OWNER_NAME,
        "npm": "2506622494",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan software dan dunia bisnis."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": OWNER_NAME,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_academics(request):
    academics = Academic.objects.annotate(
        star_count=Count("starred_by")
    ).order_by("start_year")

    context = {
        "name": OWNER_NAME,
        "academic_list": academics,
        "starred_ids": _starred_ids(request.user, "starred_academics"),
    }

    return render(request, "academics.html", context)

def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.annotate(star_count=Count("starred_by")).order_by("title")
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    context = {
        "name": OWNER_NAME,
        "project_list": projects,
        "title_query": title_query,
        "starred_ids": _starred_ids(request.user, "starred_projects"),
    }
    return render(request, "project.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects, fields=PROJECT_JSON_FIELDS, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")


def get_academics_json(request):
    academics = Academic.objects.all()
    academics_json = serializers.serialize("json", academics, fields=ACADEMIC_JSON_FIELDS, use_natural_foreign_keys=True)
    return HttpResponse(academics_json, content_type="application/json")

@role_required(can_manage)
def create_academic(request):
    form = AcademicForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat akademik berhasil ditambahkan!")
        return redirect("main:show_academics")

    context = {
        "name": OWNER_NAME,
        "form": form,
        "is_edit": False,
    }
    return render(request, "academics_form.html", context)

@role_required(can_edit)
def update_academic(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)
    form = AcademicForm(request.POST or None, instance=academic)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat akademik berhasil diperbarui!")
        return redirect("main:show_academics")

    context = {
        "name": OWNER_NAME,
        "form": form,
        "is_edit": True,
        "academic": academic,
    }
    return render(request, "academics_form.html", context)

@role_required(can_manage)
def delete_academic(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)

    if request.method == "POST":
        academic.delete()
        messages.success(request, "Riwayat akademik berhasil dihapus!")
        return redirect("main:show_academics")

    return redirect("main:show_academics")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": OWNER_NAME,
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": OWNER_NAME,
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":

        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": OWNER_NAME,
        "form": form,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def _starred_ids(user, relation):
    if not user.is_authenticated:
        return set()
    return set(getattr(user, relation).values_list("pk", flat=True))

def _toggle_star(user, obj):
    if obj.starred_by.filter(pk=user.pk).exists():
        obj.starred_by.remove(user)
    else:
        obj.starred_by.add(user)

@login_required
@require_POST
def toggle_academic_star(request, academic_id):
    _toggle_star(request.user, get_object_or_404(Academic, pk=academic_id))
    return redirect("main:show_academics")