from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Academic, Project
from main.permissions import (
    IsPortfolioOwnerOrEditorOrReadOnly,
    IsPortfolioOwnerOrReadOnly,
)
from main.serializers import AcademicSerializer, ProjectSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method == "POST":
        serializer = ProjectSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    projects = Project.objects.prefetch_related("starred_by").order_by("title", "id")
    title = request.query_params.get("title", "").strip()
    if title:
        projects = projects.filter(title__icontains=title)
    serializer = ProjectSerializer(
        projects, many=True, context={"request": request}
    )
    return Response(serializer.data)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "DELETE":
        project.delete()
        return Response(status=204)

    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    serializer = ProjectSerializer(
        project,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def academic_list(request):
    if request.method == "POST":
        serializer = AcademicSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    academics = Academic.objects.annotate(star_count=Count("starred_by")).order_by(
        "start_year"
    )
    query = request.query_params.get("q", "").strip()
    if query:
        academics = academics.filter(institution__icontains=query)
    serializer = AcademicSerializer(
        academics, many=True, context={"request": request}
    )
    return Response(serializer.data)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def academic_detail(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)
    if request.method == "DELETE":
        academic.delete()
        return Response(status=204)

    if request.method == "GET":
        serializer = AcademicSerializer(academic, context={"request": request})
        return Response(serializer.data)

    serializer = AcademicSerializer(
        academic,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def academic_star(request, academic_id):
    academic = get_object_or_404(Academic, pk=academic_id)
    if academic.starred_by.filter(pk=request.user.pk).exists():
        academic.starred_by.remove(request.user)
    else:
        academic.starred_by.add(request.user)
    return Response(
        {
            "is_starred": academic.starred_by.filter(pk=request.user.pk).exists(),
            "star_count": academic.starred_by.count(),
        }
    )
