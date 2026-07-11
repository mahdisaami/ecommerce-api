from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from authentication.serializers import RegisterSerializer, LoginSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),

        })

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid Token'},
                status=status.HTTP_400_BAD_REQUEST
            )