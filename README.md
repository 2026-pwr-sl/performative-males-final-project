# Letterboxdle - the final project of Performative Males
## Description
The project is a single player web-browser game, in which the player's goal is to guess movie titles. The system provides the player with hints such as: letterboxd movie reviews and blurred movie posters. The player has three attempts to correctky guess the movie title:
- Attempt no 1: a 5 star review, and a heavily blurred image of the movie poster
- Attempt no 2: a 3 star review, and a slightly less blurred image of the movie poster
- Attempt no 1: a 1 star review, and a lightly blurred image of the movie poster
The time to succecsully guess the title is limited to sixty seconds! The system provides two gameplay modes: classic and endless.

The user can create an account and login to it. The benefit of setting up an account is that you can see your statistics, and where you place on the leaderboard.

### Data Sources
For the purpose of populating the database with real user reviews and movie posters, we used the following datasets from Kaggle:
* Movie Reviews: [Letterboxd Movie Reviews (90,000)](https://www.kaggle.com/datasets/riyosha/letterboxd-movie-reviews-90000)
* Movie Posters & Metadata: [Letterboxd Dataset](https://www.kaggle.com/datasets/gsimonx37/letterboxd)
to fetch movies with the poster and the review use command:

```bash
    python manage.py fetch_movies
```

### Running the program
