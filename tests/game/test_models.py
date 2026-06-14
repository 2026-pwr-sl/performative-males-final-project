import pytest
from django.contrib.auth.models import User
from game.models import Movie, Profile, GameSession


@pytest.mark.django_db
def test_movie_creation_and_str():
    movie = Movie.objects.create(
        title="Pulp Fiction",
        poster_url="http://example.com/pulp.jpg",
        review_5="Masterpiece",
        review_3="Okay",
        review_1="Boring"
    )
    assert movie.title == "Pulp Fiction"
    assert str(movie) == "Pulp Fiction"


@pytest.mark.django_db
def test_profile_created_automatically_on_user_creation():
    # when creating User
    user = User.objects.create_user(
        username="testplayer",
        password="password123"
    )

    # ... the profile should be created
    assert Profile.objects.filter(user=user).exists()
    assert user.profile.high_score == 0
    assert str(user.profile) == "testplayer's Profile"


@pytest.mark.django_db
def test_game_session_str():
    user = User.objects.create_user(username="pro_gamer")
    session = GameSession.objects.create(user=user, score=120)

    # checking format
    assert "pro_gamer - Score: 120" in str(session)
