from django.urls import path

from main.views import (
    create_project,
    create_project_ajax,
    delete_project,
    get_projects_json,
    login_user,
    logout_user,
    register,
    show_academics,
    show_experience,
    show_main,
    show_projects,
    toggle_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("academics/", show_academics, name="show_academics"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/", show_projects, name="show_projects"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/", delete_project ,name="delete_project"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
]