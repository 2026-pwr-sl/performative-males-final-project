import pytest
from game.utils import get_blurred_poster

def test_get_blurred_poster_empty_url():
    # fucntion should reutnr None for an empty URL
    assert get_blurred_poster("") is None
    assert get_blurred_poster(None) is None

def test_get_blurred_poster_invalid_url():
    # function should catch an exception and return None for a corrupted link
    result = get_blurred_poster("http://strona-ktora-na-pewno-nie-istnieje.com/fake.jpg")
    assert result is None