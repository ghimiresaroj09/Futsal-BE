from django.urls import path

from accounts import views

app_name = "accounts"

auth_urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", views.ResendOTPView.as_view(), name="resend-otp"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("refresh/", views.RefreshView.as_view(), name="refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("verify-forgot-password-otp/", views.VerifyForgotPasswordOTPView.as_view(),
         name="verify-forgot-password-otp"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
]

user_urlpatterns = [
    path("me/", views.MeView.as_view(), name="me"),
]
