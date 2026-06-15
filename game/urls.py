from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import render


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
        auth_views.LogoutView.as_view(next_page="register"),
        name="logout"
    ),
    path("profile/settings/", views.profile_settings, name="profile_settings"),
    path("profile/stats/", views.profile_stats, name="profile_stats"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("game/", views.game, name="game"),
    path("result/", views.result, name="result"),
    path("game_endless/", views.game_endless, name="game_endless"),

    path("error-test/", lambda request: render(
        request,
        "game/error.html",
        {"message": "This is a test error!"}
        )),
]
