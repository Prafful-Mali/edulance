from django.shortcuts import render, redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import EmailTokenObtainPairSerializer, UserRegistrationSerializer
from django.conf import settings
from django.core.mail import send_mail
from .models import CustomUser
from .utils import generate_verification_token, verify_verification_token
from django.core.signing import SignatureExpired, BadSignature


def login_view(request):
    return render(request, 'users/login.html')

def register_view(request):
    return render(request, 'users/register.html')

def dashboard_view(request):
    return render(request, 'users/dashboard.html')


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        
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
                    subject='Verify Your Email - Edulance',
                    message=f'''
Hello {user.username},

Thank you for registering with Edulance!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Edulance Team
                    ''',
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
                return Response({"error": f"Failed to send verification email: {error_detail}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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