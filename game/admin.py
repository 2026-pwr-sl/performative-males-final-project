from django.contrib import admin
from .models import Movie, Profile


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Shows these columns in the list view
    list_display = ("title", "poster_url")
    # Adds a search bar so you can quickly find a movie by title
    search_fields = ("title",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Shows player stats right on the dashboard
    list_display = ("user", "high_score", "games_played", "longest_streak")
    # Adds a search bar to look up players by username
    search_fields = ("user__username",)
