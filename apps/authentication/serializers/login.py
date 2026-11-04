from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.services.login import authenticate_user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate_user(
            username=attrs["username"],
            password=attrs["password"],
            request=self.context.get("request"),
        )
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
