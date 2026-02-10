from rest_framework import serializers
from .models import ClientApplication

class ClientApplicationSerializer(serializers.ModelSerializer):
    services = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    services_csv = serializers.CharField(read_only=True)

    class Meta:
        model = ClientApplication
        fields = "__all__"

    def validate(self, attrs):
        # Convert services list -> csv
        services = attrs.pop("services", None)
        if services is not None:
            attrs["services_csv"] = ",".join([s.strip() for s in services if str(s).strip()])
        return attrs
