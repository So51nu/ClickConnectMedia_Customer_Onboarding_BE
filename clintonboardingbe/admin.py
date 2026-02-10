# from django.contrib import admin
# from django.utils.html import format_html
# from django.urls import reverse
# from .models import ClientApplication, CompanyProfile

# @admin.register(CompanyProfile)
# class CompanyProfileAdmin(admin.ModelAdmin):
#     list_display = ("company_name", "signature_preview")

#     def signature_preview(self, obj):
#         if obj.signature_image:
#             return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.signature_image.url)
#         return "-"
#     signature_preview.short_description = "Signature"


# @admin.register(ClientApplication)
# class ClientApplicationAdmin(admin.ModelAdmin):
#     list_display = ("id", "created_at", "orgName", "orgPAN", "orgEmail", "pdf_link")
#     search_fields = ("orgName", "orgPAN", "orgEmail", "authName", "authPAN")
#     list_filter = ("created_at",)

#     def pdf_link(self, obj):
#         url = reverse("admin_application_pdf", kwargs={"pk": obj.pk})
#         return format_html('<a href="{}" target="_blank">Download PDF</a>', url)
#     pdf_link.short_description = "PDF"
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ClientApplication, CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "signature_preview")

    def signature_preview(self, obj):
        if obj.signature_image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;border:1px solid #ddd;padding:2px;background:#fff;" />',
                obj.signature_image.url,
            )
        return "-"
    signature_preview.short_description = "Signature"


@admin.register(ClientApplication)
class ClientApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "orgName", "orgPAN", "orgEmail", "pdf_link")
    search_fields = ("orgName", "orgPAN", "orgEmail", "authName", "authPAN")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    def pdf_link(self, obj):
        """
        ✅ IMPORTANT:
        Django admin uses session auth, not JWT.
        Your `admin_application_pdf` endpoint is DRF + JWT protected,
        so admin panel cannot open it directly.

        So here we point to the PUBLIC PDF download endpoint:
        `download_application_pdf` -> /api/applications/<pk>/pdf/
        """
        url = reverse("download_application_pdf", kwargs={"pk": obj.pk})
        return format_html('<a href="{}" target="_blank" rel="noopener">Download PDF</a>', url)

    pdf_link.short_description = "PDF"

