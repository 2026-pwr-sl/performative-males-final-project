from game.utils import get_blurred_poster


def test_get_blurred_poster_empty_url():
    # function should return None for an empty URL
    assert get_blurred_poster("") is None
    assert get_blurred_poster(None) is None


def test_get_blurred_poster_invalid_url():
    # function should catch an exception and return None for corrupted link
    fake_url = "http://strona-ktora-na-pewno-nie-istnieje.com/fake.jpg"
    result = get_blurred_poster(fake_url)
    assert result is None
