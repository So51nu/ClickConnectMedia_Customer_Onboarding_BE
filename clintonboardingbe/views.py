from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ClientApplication, CompanyProfile
from .serializers import ClientApplicationSerializer
from .pdf_utils import build_application_pdf


@api_view(["POST"])
def create_application(request):
    """
    Public endpoint: accepts multipart/form-data (text + files)
    """
    serializer = ClientApplicationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    app = serializer.save()

    return Response(
        {
            "id": app.id,
            "message": "Application submitted successfully",
            "pdf_url": f"/api/applications/{app.id}/pdf/",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def download_application_pdf(request, pk: int):
    """
    Public PDF download (simple).
    If you want security later, we can add token/otp.
    """
    try:
        app = ClientApplication.objects.get(pk=pk)
    except ClientApplication.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    company = CompanyProfile.objects.first()
    company_sig_path = company.signature_image.path if company and company.signature_image else None

    pdf_bytes = build_application_pdf(app, company_signature_path=company_sig_path)
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="application_{app.id}.pdf"'
    return resp


# ---------------- ADMIN AUTH ----------------

@api_view(["POST"])
def admin_login(request):
    """
    Admin login: expects JSON {username, password}
    Only allows staff/superuser
    """
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(username=username, password=password)

    if not user or not user.is_staff:
        return Response({"detail": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response(
        {"access": str(refresh.access_token), "refresh": str(refresh)},
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_list_applications(request):
    if not request.user.is_staff:
        return Response({"detail": "Forbidden"}, status=403)

    qs = ClientApplication.objects.order_by("-created_at")[:500]
    data = []
    for a in qs:
        data.append({
            "id": a.id,
            "created_at": a.created_at.isoformat(),
            "orgName": a.orgName,
            "orgPAN": a.orgPAN,
            "orgEmail": a.orgEmail,
            "authName": a.authName,
            "pdf_url": f"/api/admin/applications/{a.id}/pdf/",
        })
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_application_detail(request, pk: int):
    if not request.user.is_staff:
        return Response({"detail": "Forbidden"}, status=403)

    try:
        app = ClientApplication.objects.get(pk=pk)
    except ClientApplication.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    serializer = ClientApplicationSerializer(app)
    out = serializer.data
    out["services"] = app.services_list()

    # Return absolute media URLs if needed by frontend
    def file_url(f):
        try:
            return f.url if f else None
        except Exception:
            return None

    out["authPanFront_url"] = file_url(app.authPanFront)
    out["authPanBack_url"] = file_url(app.authPanBack)
    out["authAadhaarFront_url"] = file_url(app.authAadhaarFront)
    out["authAadhaarBack_url"] = file_url(app.authAadhaarBack)
    out["applicantSignatureFile_url"] = file_url(app.applicantSignatureFile)
    out["companySignatureFile_url"] = file_url(app.companySignatureFile)

    return Response(out)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_application_pdf(request, pk: int):
    if not request.user.is_staff:
        return Response({"detail": "Forbidden"}, status=403)

    try:
        app = ClientApplication.objects.get(pk=pk)
    except ClientApplication.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    company = CompanyProfile.objects.first()
    company_sig_path = company.signature_image.path if company and company.signature_image else None

    pdf_bytes = build_application_pdf(app, company_signature_path=company_sig_path)
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="application_{app.id}.pdf"'
    return resp

@api_view(["GET"])
def public_company_signature(request):
    """
    Public endpoint: returns company signature image URL (if uploaded by admin)
    """
    company = CompanyProfile.objects.first()
    if not company or not company.signature_image:
        return Response(
            {
                "company_name": company.company_name if company else "Click Connect Media Pvt. Ltd.",
                "signature_url": None,
            },
            status=200,
        )

    return Response(
        {
            "company_name": company.company_name,
            "signature_url": request.build_absolute_uri(company.signature_image.url),
        },
        status=200,
    )
