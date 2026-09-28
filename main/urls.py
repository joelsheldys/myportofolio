from django.urls import path

from main.views import get_projects_json, show_main, show_experience, show_academics, show_projects, create_project, delete_project, create_academic, update_academic, delete_academic, get_academics_json, register, login_user, logout_user, toggle_star, toggle_academic_star

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("academics/", show_academics, name="show_academics"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/", show_projects, name="show_projects"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/", delete_project ,name="delete_project"),
    path("academics/add/", create_academic, name="create_academic"),
    path("academics/<uuid:academic_id>/edit/", update_academic, name="update_academic"),
    path("academics/<uuid:academic_id>/delete/", delete_academic, name="delete_academic"),
    path("api/academics/", get_academics_json, name="get_academics_json"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    path("academics/<uuid:academic_id>/star/", toggle_academic_star, name="toggle_academic_star"),
]