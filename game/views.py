from random import sample, choice

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Movie
from .utils import get_blurred_poster


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "game/register.html", {"form": form})


@login_required
def profile_settings(request):
    if request.method == "POST":
        if "update_profile" in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=request.user.profile
            )

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                return redirect("profile")

        elif "delete_account" in request.POST:
            user = request.user
            logout(request)
            user.delete()
            return redirect("register")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "game/profile.html", context)


def game(request):
    if "movie_ids" not in request.session:
        # movies = list(Movie.objects.values_list("id", flat=True))

        # Excluded movies without poster
        movies = list(
            Movie.objects.exclude(poster_url='').values_list("id", flat=True)
            )

        # starting state for the game
        selected_movies = sample(movies, min(10, len(movies)))
        request.session["movie_ids"] = selected_movies
        request.session["filter_styles"] = [
            choice(['blur', 'pixel'])for _ in range(len(selected_movies))]
        request.session["round"] = 0
        request.session["attempt"] = 1
        request.session["score"] = 0

        # previous movie
        request.session["prev_result"] = None
        request.session["prev_movie"] = None

    movie_ids = request.session["movie_ids"]
    round_idx = request.session["round"]

    # game over
    if round_idx >= len(movie_ids):
        score = request.session["score"]

        request.session.flush()

        return render(request, "game/game_over.html",
                      {"score": score})

    movie = Movie.objects.get(id=movie_ids[round_idx])

    # handle guess submission
    if request.method == "POST":
        guess = request.POST.get("guess", "").strip()

        # handle previous guess feedback
        correct = guess.lower() == movie.title.lower()

        request.session["last_correct"] = correct
        request.session["last_movie"] = movie.title
        request.session["last_guess"] = guess
        request.session["last_poster"] = movie.poster_url

        if correct:
            request.session["score"] += 1
            request.session["round"] += 1
            request.session["attempt"] = 1

            return redirect("result")

        else:
            request.session["attempt"] += 1

            if request.session["attempt"] > 3:
                request.session["round"] += 1
                request.session["attempt"] = 1
                return redirect("result")

        return redirect("game")

    # Apply filter to the poster
    current_attempt = request.session["attempt"]
    # Filter levels: 0-none, 1-low, 2-medium, 3-high
    # Filter types: 'blur', 'pixel'
    filter_level = 3 - (current_attempt - 1)  # we have 3 attemps max
    filter_styles = request.session.get("filter_styles", [])
    filter_type = filter_styles[round_idx]
    blurred_image_url = get_blurred_poster(movie.poster_url, filter_level,
                                           filter_type=filter_type)

    return render(request, "game/game.html", {
        "movie": movie,
        "round": round_idx + 1,
        "attempt": request.session["attempt"],
        "score": request.session["score"],
        "poster_url": blurred_image_url
        })


def result(request):

    # if entered without playing a round, redirect to game
    if "last_movie" not in request.session:
        return redirect("game")

    # next round
    if request.method == "POST":
        request.session.pop("last_movie", None)
        request.session.pop("last_guess", None)
        request.session.pop("last_correct", None)
        request.session.pop("last_poster", None)

        movie_ids = request.session.get("movie_ids", [])
        round_index = request.session.get("round", 0)

        if round_index >= len(movie_ids):
            score = request.session.get("score", 0)

            request.session.flush()

            return render(request, "game/game_over.html", {
                "score": score
            })

        return redirect("game")

    return render(request, "game/result.html", {
        "movie": request.session["last_movie"],
        "guess": request.session["last_guess"],
        "correct": request.session["last_correct"],
        "poster_url": request.session.get("last_poster"),
    })
