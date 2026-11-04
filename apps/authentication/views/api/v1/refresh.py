from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
