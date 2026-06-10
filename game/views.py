from random import sample

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Movie


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
        movies = list(Movie.objects.values_list("id", flat=True))

        # starting state for the game
        request.session["movie_ids"] = sample(movies, min(10, len(movies)))
        request.session["round"] = 0
        request.session["attempt"] = 1
        request.session["score"] = 0

        # previous movie
        request.session["prev_result"] = None
        request.session["prev_movie"] = None

        #total time left
        request.session["time_remaining"] = 30

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

        #update time left
        time_left = int(request.POST.get("time_remaining",0))
        request.session["time_remaining"] = time_left

        # handle previous guess feedback
        correct = guess.lower() == movie.title.lower()

        request.session["last_correct"] = correct
        request.session["last_movie"] = movie.title
        request.session["last_guess"] = guess

        if correct:
            request.session["score"] += 1
            request.session["round"] += 1
            request.session["attempt"] = 1

            request.session["time_remaining"] = 30


            return redirect("result")

        else:
            request.session["attempt"] += 1

            if request.session["attempt"] > 3 or time_left <= 0:
                request.session["round"] += 1
                request.session["attempt"] = 1

                request.session["time_remaining"] = 30

                return redirect("result")

        return redirect("game")

    return render(request, "game/game.html", {
        "movie": movie,
        "round": round_idx + 1,
        "attempt": request.session["attempt"],
        "score": request.session["score"],
        "time_remaining": request.session.get("time_remaining", 30),
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
    })
