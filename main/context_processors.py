def roles(request):
    user = request.user
    editor = user.is_authenticated and user.groups.filter(name="Editor").exists()
    return {
        "is_editor": editor,
        "can_edit": user.is_superuser or editor,
        "can_manage": user.is_superuser,
    }