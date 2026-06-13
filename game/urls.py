from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("register/", views.register, name="register"),
    # builtin
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="game/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout"
    ),
    path("profile/", views.profile_settings, name="profile"),
    path("profile/stats/", views.profile_stats, name="profile_stats"),
    path("", views.register, name="home"),
    path("game/", views.game, name="game"),
    path("result/", views.result, name="result"),
]
