import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Movie

@pytest.mark.django_db
def test_register_page_loads(client):
    # Check if register returns code 200 (OK)
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Create an Account" in response.content # check if the text is in html

@pytest.mark.django_db
def test_profile_view_redirects_unauthenticated_user(client):
    # logged out user tries to enter profile
    url = reverse('profile')
    response = client.get(url)
    
    # kick him (code 302 - Redirect)
    assert response.status_code == 302
    assert "login" in response.url

@pytest.mark.django_db
def test_leaderboard_page_loads(client):
    # a logged out user can see the ranking
    url = reverse('leaderboard')
    response = client.get(url)
    
    assert response.status_code == 200
    assert b"Global Leaderboard" in response.content

@pytest.mark.django_db
def test_game_initialization(client):
    # create 10 movies for the sample() function in views.py
    for i in range(10):
        Movie.objects.create(
            title=f"Test Movie {i}",
            poster_url="http://example.com/poster.jpg",
            review_5="Great", review_3="Ok", review_1="Bad"
        )
    
    url = reverse('game')
    response = client.get(url)
    
    assert response.status_code == 200
    
    # check if game correctly loaded session variables
    session = client.session
    assert "movie_ids" in session
    assert len(session["movie_ids"]) == 10
    assert session["round"] == 0
    assert session["score"] == 0
    assert session["attempt"] == 1
    assert session["time_remaining"] == 30

@pytest.mark.django_db
def test_result_redirects_if_no_game_played(client):
    # if someone tries to enter /result/ without playing...
    url = reverse('result')
    response = client.get(url)
    
    # -> hey should be redirected back to the game
    assert response.status_code == 302
    assert response.url == reverse('game')

@pytest.mark.django_db
def test_correct_guess_logic(client):
    # Create a single movie for the test
    movie = Movie.objects.create(
        title="Inception",
        poster_url="http://example.com/poster.jpg",
        review_5="Dream", review_3="Ok", review_1="Bad"
    )
    
    # manually set session to simulate mid-game state
    session = client.session
    session["movie_ids"] = [movie.id]
    session["round"] = 0
    session["attempt"] = 1
    session["score"] = 0
    session["filter_styles"] = ["blur"]
    session.save()
    
    # send POST request with correct guess
    url = reverse('game')
    response = client.post(url, {
        "guess": "Inception",
        "time_remaining": "25"
    })
    
    # should redirect to result page
    assert response.status_code == 302
    assert response.url == reverse('result')
    
    # is score increased correctly (10 base + 5 time bonus = 15)
    updated_session = client.session
    assert updated_session["last_correct"] is True
    assert updated_session["score"] == 15
