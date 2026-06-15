# Letterboxdle - the final project of Performative Males
## Description
The project is a single player web-browser game, in which the player's goal is to guess movie titles. The system provides the player with hints such as: letterboxd movie reviews and blurred movie posters. The player has three attempts to correctky guess the movie title:
- Attempt no 1: a 5 star review, and a heavily blurred image of the movie poster
- Attempt no 2: a 3 star review, and a slightly less blurred image of the movie poster
- Attempt no 1: a 1 star review, and a lightly blurred image of the movie poster
The time to succecsully guess the title is limited to sixty seconds! The system provides two gameplay modes: classic and endless.
The user can create an account and login to it. The benefit of setting up an account is that you can see your statistics, and where you place on the leaderboard.
### Database diagram ( generated with `dbdiagram.io`)

<img width="812" height="586" alt="Untitled" src="https://github.com/user-attachments/assets/47d7b3c7-b092-4424-9107-9abcb1c27f4c" />


## Screenshots

### Home page: 

<img width="960" height="504" alt="image" src="https://github.com/user-attachments/assets/94c6b008-dcd7-41b5-b639-4a137576fd03" />

### Main Gameplay:

<img width="1861" height="946" alt="image" src="https://github.com/user-attachments/assets/82b7fb56-1503-410f-9e6f-df3e83452e64" />
<img width="1862" height="942" alt="image" src="https://github.com/user-attachments/assets/3ea66624-b8b5-465e-9434-4852be8a80e0" />
<img width="1853" height="938" alt="image" src="https://github.com/user-attachments/assets/905cf804-2c41-44c3-a2cd-c75e4d940262" />

### End of game:

<img width="1851" height="940" alt="image" src="https://github.com/user-attachments/assets/d30c1a82-2083-42ba-9299-a2218c58c9d2" />

### Register and login:

<img width="948" height="437" alt="image" src="https://github.com/user-attachments/assets/bfb00f6a-0688-4b82-a704-48a6b17881be" />
<img width="943" height="433" alt="image" src="https://github.com/user-attachments/assets/05471993-e7b2-4379-8fc4-ee953b4d3da4" />


### Leaderboad: 

<img width="940" height="437" alt="image" src="https://github.com/user-attachments/assets/83152da2-52ab-4a1e-ab0d-7a9a5ccd4821" />





### Data Sources
For the purpose of populating the database with real user reviews and movie posters, we used the following datasets from Kaggle:
* Movie Reviews: [Letterboxd Movie Reviews (90,000)](https://www.kaggle.com/datasets/riyosha/letterboxd-movie-reviews-90000)
* Movie Posters & Metadata: [Letterboxd Dataset](https://www.kaggle.com/datasets/gsimonx37/letterboxd)
to fetch movies with the poster and the review use command:

```bash
    python manage.py fetch_movies
```

## Running the program

Follow these steps to get the Letterboxdle game running locally on your machine.

### 1. Set up the Virtual Environment
It's highly recommended to use a virtual environment to keep dependencies clean. Open your terminal in the project directory and run:
```bash
python -m venv .venv
```
Activate the virtual environment:
- Windows: .venv\Scripts\activate
- Mac/Linux: source .venv/bin/activate
### 2. Install Dependencies
With your virtual environment active, install all required packages (including Django, Pytest, and Pillow for image processing):
``` bash
pip install -r requirements.txt
```
### 3. Apply Migrations
Set up the local SQLite database by applying the necessary migrations for models and sessions:
```bash
python manage.py migrate
```
### 4. Populate the database
To actually play the game, you need movies! Use our custom script to fetch real Letterboxd reviews and posters. It will automatically download the data, apply the blur/pixel filters, and censor movie titles and profanities from the text:
```bash
python manage.py fetch_movies
```
### 5. Run the server
```bash
python manage.py runserver
```
Open your browser and navigate to http://127.0.0.1:8000/. You're ready to play! Enjoy!
### Extra!
If you want to test out the admin privilleges, create your superaccount:
```bash
python manage.py createsuperuser
```
And to run the tests:
```bash
pytest
```

## Work division
- Kamil Borkowski - main gameplay logic; endless mode gameplay logic; scoring system; frontend of the game view
- Borys Dąbrowski - autocomplete of answers; match history and leaderboard logic with frontend; image blurring utility;
- Oliwier Krawczyk - setting up the skeleton of the project; creation of basic models; admin panel; addition of timer logic; setting up tests;
- Timoteo Lema - fetching of movie data; frontend of login page, register page, home page, profile page;

  Additionally all of the team members have took part in field testing and troubleshooting.
