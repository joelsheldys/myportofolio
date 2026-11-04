from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Academic, Project


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
            "star_count",
            "is_starred",
            "starred_by_names",
        )
        read_only_fields = ("id", "star_count", "is_starred", "starred_by_names")

    def validate_title(self, value):
        title = strip_tags(value).strip()
        if not title:
            raise serializers.ValidationError(
                "Nama proyek tidak boleh hanya berisi tag HTML."
            )
        return title

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate_tech_stack(self, value):
        return strip_tags(value).strip()

    def validate_project_url(self, value):
        return self._validate_http_url(value)

    def validate_project_image_url(self, value):
        return self._validate_http_url(value)

    @staticmethod
    def _validate_http_url(value):
        if value and not value.lower().startswith(("http://", "https://")):
            raise serializers.ValidationError("URL harus menggunakan HTTP atau HTTPS.")
        return value

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.starred_by.filter(pk=request.user.pk).exists()
        )

    def get_starred_by_names(self, obj):
        return ", ".join(obj.starred_by.values_list("username", flat=True))


class AcademicSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    period = serializers.CharField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Academic
        fields = (
            "id",
            "institution",
            "level",
            "level_display",
            "start_year",
            "end_year",
            "period",
            "star_count",
            "is_starred",
        )
        read_only_fields = (
            "id",
            "level_display",
            "period",
            "star_count",
            "is_starred",
        )

    def validate_institution(self, value):
        institution = strip_tags(value).strip()
        if not institution:
            raise serializers.ValidationError(
                "Nama institusi tidak boleh hanya berisi tag HTML."
            )
        return institution

    def validate(self, attrs):
        start_year = attrs.get(
            "start_year",
            self.instance.start_year if self.instance else None,
        )
        end_year = attrs.get(
            "end_year",
            self.instance.end_year if self.instance else None,
        )
        if start_year and end_year and end_year < start_year:
            raise serializers.ValidationError(
                {"end_year": "Tahun selesai tidak boleh lebih awal dari tahun mulai."}
            )
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.starred_by.filter(pk=request.user.pk).exists()
        )
