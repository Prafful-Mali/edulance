from django.shortcuts import render, redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import EmailLoginSerializer, UserRegistrationSerializer, UserProfileSerializer, PasswordChangeSerializer
from django.conf import settings
from rest_framework.decorators import action
from django.core.mail import send_mail
from .models import CustomUser
from .utils import generate_verification_token, verify_verification_token
from django.core.signing import SignatureExpired, BadSignature
from .constants import EMAIL_VERIFICATION_SUBJECT, EMAIL_VERIFICATION_MESSAGE



def login_view(request):
    return render(request, 'users/login.html')

def register_view(request):
    return render(request, 'users/register.html')

def dashboard_view(request):
    return render(request, 'users/dashboard.html')


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = EmailLoginSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = serializer.validated_data
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        
        return Response({
            "message": "Login successful",
            "access": access_token,
            "refresh": refresh_token
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = generate_verification_token(user)
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"            
            try:
                send_mail(
                    subject=EMAIL_VERIFICATION_SUBJECT,
                    message=EMAIL_VERIFICATION_MESSAGE.format(
                        username=user.username,
                        verification_url=verification_url
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                return Response({
                    "message": "Registration successful! Please check your email to verify your account.",
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                error_detail = str(e)
                user.delete()
                return Response({
                    "error": f"Failed to send verification email: {error_detail}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        try:
            user_id, email = verify_verification_token(token, max_age=86400) 
            user = CustomUser.objects.get(id=user_id, email=email)
            
            if user.is_email_verified:
                return redirect('/login/?message=already_verified')
           
            user.is_email_verified = True
            user.save()
            
            return redirect('/login/?message=verified')
            
        except SignatureExpired:
            return redirect('/login/?message=expired')
            
        except BadSignature:
            return redirect('/login/?message=invalid')
            
        except CustomUser.DoesNotExist:
            return redirect('/login/?message=not_found')
            
        except Exception as e:
            return redirect('/login/?message=error')
        
class CustomTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token required in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            
            refresh.set_jti()
            refresh.set_exp()
            new_refresh = str(refresh)

            return Response({
                "access": new_access,
                "refresh": new_refresh,
                "message": "Token refreshed successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Logout successful"}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": "Invalid or expired token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
                
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)
    
    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response(
                {"error": "Only admins can list all users"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role != 'admin' and request.user.id != instance.id:
            return Response(
                {"error": "You can only delete your own account"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role != 'admin' and request.user.id != instance.id:
            return Response(
                {"error": "You can only update your own account"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                "message": "Password changed successfully"
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)