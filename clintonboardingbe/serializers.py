from rest_framework import serializers
from .models import ClientApplication


class ClientApplicationSerializer(serializers.ModelSerializer):
    # incoming from frontend (multipart): services will come as repeated keys
    services = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    services_csv = serializers.CharField(read_only=True)

    class Meta:
        model = ClientApplication
        fields = "__all__"

    def validate(self, attrs):
        """
        ✅ Important fix:
        multipart/form-data me services repeated keys hoti hain,
        e.g. services=bulk-whatsapp, services=rcs-sms...
        DRF ListField hamesha list nahi banata.

        So we pull from self.initial_data.getlist('services') if available.
        """
        services = attrs.pop("services", None)

        # If multipart QueryDict -> use getlist
        initial = getattr(self, "initial_data", None)
        if initial is not None and hasattr(initial, "getlist"):
            services_from_form = initial.getlist("services")
            if services_from_form:
                services = services_from_form

        # Normalize
        final_services = []
        if services:
            for s in services:
                ss = str(s).strip()
                if ss:
                    final_services.append(ss)

        attrs["services_csv"] = ",".join(final_services)
        return attrs
