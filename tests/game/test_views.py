import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register_page_loads(client):
    # Check if register returns code 200 (OK)
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Create an Account" in response.content # check if the te xt id in html

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