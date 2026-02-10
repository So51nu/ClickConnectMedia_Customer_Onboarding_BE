from django.urls import path
from .views import (
    create_application,
    download_application_pdf,
    admin_login,
    admin_list_applications,
    admin_application_detail,
    admin_application_pdf,
    public_company_signature,
)

urlpatterns = [
    # Public (user submit)
    path("applications/", create_application, name="create_application"),
    path("applications/<int:pk>/pdf/", download_application_pdf, name="download_application_pdf"),
    path("company-signature/", public_company_signature, name="public_company_signature"),
    # Admin (JWT)
    path("admin/login/", admin_login, name="admin_login"),
    path("admin/applications/", admin_list_applications, name="admin_list_applications"),
    path("admin/applications/<int:pk>/", admin_application_detail, name="admin_application_detail"),
    path("admin/applications/<int:pk>/pdf/", admin_application_pdf, name="admin_application_pdf"),
]
