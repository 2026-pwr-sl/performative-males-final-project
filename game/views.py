import csv
from random import sample, choice

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Count
from django.http import JsonResponse, HttpResponse
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Movie, GameSession, Profile
from .utils import get_blurred_poster


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # return redirect("home") we do not have home yet :c
            return redirect("login")
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
                return redirect("profile_settings")

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
    # Autocomplete functionality
    if request.method == "GET" and "q" in request.GET:
        query = request.GET.get('q', '')
        if query:
            # Case-insensitive
            movies = Movie.objects.exclude(poster_url='').filter(
                title__icontains=query
            ).values_list('title', flat=True)[:7]
            return JsonResponse({'suggestions': list(movies)})
        return JsonResponse({'suggestions': []})

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

        # total time left
        request.session["time_remaining"] = 60

    movie_ids = request.session["movie_ids"]
    round_idx = request.session["round"]

    # game over
    if round_idx >= len(movie_ids):
        score = request.session.get("score", 0)

        finalize_game_session(request, score)

        return render(request, "game/game_over.html",
                      {"score": score})

    movie = Movie.objects.get(id=movie_ids[round_idx])

    # handle guess submission
    if request.method == "POST":
        guess = request.POST.get("guess", "").strip()

        # update time left
        time_left = int(request.POST.get("time_remaining", 0))
        request.session["time_remaining"] = time_left

        # handle previous guess feedback
        correct = guess.lower() == movie.title.lower()

        request.session["gained_score"] = 0
        request.session["last_correct"] = correct
        request.session["last_movie"] = movie.title
        request.session["last_guess"] = guess
        request.session["last_poster"] = movie.poster_url

        if correct:
            # SCORING SYSTEM RULES
            # MAX SCORE PER ROUND: 15 points
            # 1st attempt: 10 points
            # 2nd attempt: 6 points
            # 3rd attempt: 2 points
            # TIME BONUS
            # 1 point for every 10 seconds remaining (max 6 points)
            gained_score = 10 - (request.session["attempt"] - 1) * 4
            gained_score += min(6, time_left // 10)

            request.session["gained_score"] = gained_score

            request.session["score"] += request.session["gained_score"]
            request.session["round"] += 1
            request.session["attempt"] = 1

            request.session["time_remaining"] = 60

            return redirect("result")

        else:
            request.session["attempt"] += 1

            if request.session["attempt"] > 3 or time_left <= 0:
                request.session["round"] += 1
                request.session["attempt"] = 1

                request.session["time_remaining"] = 60

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
        "time_remaining": request.session.get("time_remaining", 60),
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

            finalize_game_session(request, score)

            return render(request, "game/game_over.html", {
                "score": score
            })

        return redirect("game")

    return render(request, "game/result.html", {
        "movie": request.session["last_movie"],
        "guess": request.session["last_guess"],
        "correct": request.session["last_correct"],
        "poster_url": request.session.get("last_poster"),
        "gained_score": request.session.get("gained_score", 0)
    })


def finalize_game_session(request, score):
    if request.user.is_authenticated:
        # Save current game session
        GameSession.objects.create(user=request.user, score=score)

        # Update profile stats
        profile = request.user.profile
        profile.games_played += 1
        if score > profile.high_score:
            profile.high_score = score
        profile.save()

    # Clear game-related session variables
    game_keys = ["movie_ids", "filter_styles", "round", "attempt", "score",
                 "prev_result", "prev_movie", "time_remaining", "last_movie",
                 "last_guess", "last_correct", "last_poster", "gained_score"]
    for key in game_keys:
        request.session.pop(key, None)


def game_endless(request):
    # Autocomplete functionality
    if request.method == "GET" and "q" in request.GET:
        query = request.GET.get('q', '')
        if query:
            # Case-insensitive
            movies = Movie.objects.exclude(poster_url='').filter(
                title__icontains=query
            ).values_list('title', flat=True)[:7]
            return JsonResponse({'suggestions': list(movies)})
        return JsonResponse({'suggestions': []})

    if "attempt_endless" not in request.session:
        request.session["attempt_endless"] = 0
        request.session["streak_endless"] = 0

    if request.session["attempt_endless"] == 0:
        request.session["attempt_endless"] = 1
        # movies = list(Movie.objects.values_list("id", flat=True))

        # Excluded movies without poster
        movies = list(
            Movie.objects.exclude(poster_url='').values_list("id", flat=True)
            )

        # starting state for the game
        request.session["movie_id_endless"] = choice(movies)
        movie_id = request.session["movie_id_endless"]
        request.session["filter_type_endless"] = choice(['blur', 'pixel'])

        # total time left
        request.session["time_remaining_endless"] = 60
    else:
        movie_id = request.session.get("movie_id_endless")

    if not movie_id:
        request.session["attempt_endless"] = 1
        return redirect("game_endless")

    movie = Movie.objects.get(id=movie_id)

    # handle guess submission
    if request.method == "POST":
        guess = request.POST.get("guess", "").strip()

        # update time left
        time_left = int(request.POST.get("time_remaining", 0))
        request.session["time_remaining_endless"] = time_left

        # handle previous guess feedback
        correct = guess.lower() == movie.title.lower()

        request.session["gained_score_endless"] = 0
        request.session["last_correct_endless"] = correct
        request.session["last_movie_endless"] = movie.title
        request.session["last_guess_endless"] = guess
        request.session["last_poster_endless"] = movie.poster_url

        if correct:
            request.session["streak_endless"] += 1
            request.session["attempt_endless"] = 0

            request.session.pop("movie_id_endless", None)

            return redirect("game_endless")

        else:
            request.session["attempt_endless"] += 1

            if request.session["attempt_endless"] > 3 or time_left <= 0:
                final_streak = request.session.get("streak_endless", 0)

                finalize_endless(request, streak=final_streak)

                return render(request, "game/game_over_endless.html", {
                    "movie": movie,
                    "streak": final_streak,
                    "poster_url": movie.poster_url,
                    })

        return redirect("game_endless")

    # Apply filter to the poster
    current_attempt = request.session["attempt_endless"]
    # Filter levels: 0-none, 1-low, 2-medium, 3-high
    # Filter types: 'blur', 'pixel'
    filter_level = 3 - (current_attempt - 1)  # we have 3 attemps max
    filter_type = request.session.get("filter_type_endless", "blur")
    blurred_image_url = get_blurred_poster(movie.poster_url, filter_level,
                                           filter_type=filter_type)

    return render(request, "game/game_endless.html", {
        "movie": movie,
        "streak": request.session.get("streak_endless", 0),
        "attempt": current_attempt,
        "time_remaining": request.session.get("time_remaining_endless", 60),
        "poster_url": blurred_image_url
        })


def finalize_endless(request, streak):
    if request.user.is_authenticated:
        # Save current game session
        GameSession.objects.create(
            user=request.user, score=streak, endless_mode=True
            )

        # Update profile stats
        profile = request.user.profile
        profile.games_played += 1
        if streak > profile.longest_streak:
            profile.longest_streak = streak
        profile.save()

    # Clear game-related session variables
    game_keys = [
            "movie_id_endless",
            "filter_type_endless",
            "streak_endless",
            "attempt_endless",
            "time_remaining_endless",
            "last_movie_endless",
            "last_guess_endless",
            "last_correct_endless",
            "last_poster_endless",
            "gained_score_endless"
        ]
    for key in game_keys:
        request.session.pop(key, None)


@login_required
def profile_stats(request):
    try:
        # Fetch the 10 most recent games
        classic_games_qs = (
            GameSession.objects
            .filter(user=request.user, endless_mode=False)
            .order_by('-date_played')[:10]
        )
        classic_games = list(classic_games_qs)[::-1]

        endless_games_qs = (
            GameSession.objects
            .filter(user=request.user, endless_mode=True)
            .order_by('-date_played')[:10]
        )
        endless_games = list(endless_games_qs)[::-1]
        # Reverse to chronological order

        # Handle CSV Download
        if request.GET.get('download') == 'csv':
            mode = request.GET.get('mode', 'classic')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                f'attachment; filename="my_latest_{mode}_scores.csv"'
                )

            writer = csv.writer(response)
            writer.writerow([
                'Playthrough', 'Score', 'Game Mode', 'Date Played'
                ])

            if mode == 'endless':
                export_games = endless_games
            else:
                export_games = classic_games

            for index, game in enumerate(export_games, start=1):
                writer.writerow([
                    index,
                    game.score,
                    "Endless" if game.endless_mode else "Classic",
                    game.date_played.strftime('%Y-%m-%d %H:%M')
                ])

            return response

        # Prepare Data for Chart.js

        classic_stats = (
            GameSession.objects
            .filter(user=request.user, endless_mode=False)
            .aggregate(total=Count('id'), best=Max('score'))
        )
        classic_total = classic_stats['total'] or 0
        classic_best = classic_stats['best'] or 0

        endless_stats = (
            GameSession.objects
            .filter(user=request.user, endless_mode=True)
            .aggregate(total=Count('id'), best=Max('score'))
        )
        endless_total = endless_stats['total'] or 0
        endless_best = endless_stats['best'] or 0

        classic_scores = [game.score for game in classic_games]
        classic_labels = [f"Game {i+1}" for i in range(len(classic_scores))]

        endless_scores = [game.score for game in endless_games]
        endless_labels = [f"Game {i+1}" for i in range(len(endless_scores))]

        context = {
            "classic_scores": classic_scores,
            "classic_labels": classic_labels,
            "endless_scores": endless_scores,
            "endless_labels": endless_labels,
            "classic_total": classic_total,
            "classic_best": classic_best,
            "endless_total": endless_total,
            "endless_best": endless_best,
            "best_score": request.user.profile.high_score,
            "has_classic_data": len(classic_scores) > 0,
            "has_endless_data": len(endless_scores) > 0,
            "has_data": (len(classic_scores) > 0 or len(endless_scores) > 0)
        }
        return render(request, "game/stats.html", context)

    except Exception as e:
        return render(
            request,
            "game/error.html",
            {"message": f"Could not load stats: {str(e)}"}
            )


def leaderboard(request):
    try:
        # Fetch top 10 profiles with the highest high_score
        top_players = (
            Profile.objects.
            select_related('user').
            order_by('-high_score')[:10]
            )

        context = {
            "top_players": top_players
        }
        return render(request, "game/leaderboard.html", context)

    except Exception as e:
        return render(
            request,
            "game/error.html",
            {"message": f"Could not load leaderboard: {str(e)}"}
            )
@login_required
def home(request):
    return render(request, "game/home.html")