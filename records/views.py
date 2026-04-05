from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema  # ← ADD THIS

from .models import FinancialRecord
from .serializers import (
    RecordCreateSerializer,
    RecordReadSerializer,
    RecordUpdateSerializer,
)
from .filters import FinancialRecordFilter
from users.permissions import IsAdmin, IsAdminOrAnalyst


class RecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def get_active_records():
    """Base queryset — always excludes soft deleted records."""
    return FinancialRecord.objects.filter(is_deleted=False)


class RecordListCreateView(APIView):
    """
    GET  /api/records/  → Admin + Analyst. List records with filtering + pagination.
    POST /api/records/  → Admin only. Create a new financial record.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAdminOrAnalyst()]

    def get(self, request):
        queryset = get_active_records()

        filterset = FinancialRecordFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response({
                "success": False,
                "error": filterset.errors,
                "code": 400
            }, status=400)

        filtered_qs = filterset.qs

        paginator = RecordPagination()
        page = paginator.paginate_queryset(filtered_qs, request)

        serializer = RecordReadSerializer(page, many=True)

        return Response({
            "success": True,
            "data": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data
            }
        }, status=200)

    @swagger_auto_schema(request_body=RecordCreateSerializer)  # ← ADD THIS
    def post(self, request):
        serializer = RecordCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            record = serializer.save()
            return Response({
                "success": True,
                "message": "Financial record created successfully.",
                "data": RecordReadSerializer(record).data
            }, status=201)

        return Response({
            "success": False,
            "error": serializer.errors,
            "code": 400
        }, status=400)


class RecordDetailView(APIView):
    """
    GET    /api/records/<pk>/  → Admin + Analyst.
    PATCH  /api/records/<pk>/  → Admin only.
    DELETE /api/records/<pk>/  → Admin only. Soft delete.
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrAnalyst()]
        return [IsAdmin()]

    def get_object(self, pk):
        try:
            return get_active_records().get(pk=pk)
        except FinancialRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        record = self.get_object(pk)
        if not record:
            return Response({
                "success": False,
                "error": "Financial record not found.",
                "code": 404
            }, status=404)

        return Response({
            "success": True,
            "data": RecordReadSerializer(record).data
        }, status=200)

    @swagger_auto_schema(request_body=RecordUpdateSerializer)  # ← ADD THIS
    def patch(self, request, pk):
        record = self.get_object(pk)
        if not record:
            return Response({
                "success": False,
                "error": "Financial record not found.",
                "code": 404
            }, status=404)

        serializer = RecordUpdateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Financial record updated successfully.",
                "data": RecordReadSerializer(record).data
            }, status=200)

        return Response({
            "success": False,
            "error": serializer.errors,
            "code": 400
        }, status=400)

    def delete(self, request, pk):
        record = self.get_object(pk)
        if not record:
            return Response({
                "success": False,
                "error": "Financial record not found.",
                "code": 404
            }, status=404)

        record.is_deleted = True
        record.save()

        return Response({
            "success": True,
            "message": "Financial record deleted successfully."
        }, status=200)