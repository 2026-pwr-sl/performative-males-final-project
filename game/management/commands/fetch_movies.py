import csv
import os
import re
import json
from django.core.management.base import BaseCommand
from game.models import Movie
from django.conf import settings


def normalize_title(title):
    # Usuwa wszystko co nie jest literą lub cyfrą (spacje, myślniki, dwukropki)
    return re.sub(r'[^a-z0-9]', '', str(title).lower())


def load_json_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("words", [])
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return []


def censor_review(review, title, words_to_censor=None):
    title_pattern = re.escape(title)
    censored_review = re.sub(
        title_pattern,
        "[MOVIE TITLE]",
        review,
        flags=re.IGNORECASE
        )

    # censor words from list
    if words_to_censor:
        joined_words = "|".join([re.escape(w) for w in words_to_censor])
        words_pattern = rf"({joined_words})"

        def replace_with_stars(match):
            return "*" * len(match.group(0))

        censored_review = re.sub(
            words_pattern,
            replace_with_stars,
            censored_review,
            flags=re.IGNORECASE
        )

    return censored_review


class Command(BaseCommand):
    help = "fetch movie titles with posters and reviews."

    def handle(self, *args, **kwargs):
        # Ścieżki do plików
        movies_csv_path = os.path.join(settings.BASE_DIR, 'movies.csv')
        posters_csv_path = os.path.join(settings.BASE_DIR, 'posters.csv')
        reviews_csv_path = os.path.join(
            settings.BASE_DIR, 'letterboxd_250movie_reviews.csv'
        )

        self.stdout.write("1. Loading posters...")
        posters_dict = {}
        with open(posters_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                posters_dict[row['id']] = row['link']

        self.stdout.write("2. Loading movies...")
        movies_info = {}
        with open(movies_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = row['id']
                title = row['name']
                if movie_id in posters_dict:
                    norm_title = normalize_title(title)
                    movies_info[norm_title] = {
                        'real_title': title,
                        'poster': posters_dict[movie_id]
                    }

        msg = f"  -> Matched posters to {len(movies_info)} movies."
        self.stdout.write(msg)
        self.stdout.write("3. Searching reviews...)")

        movies_to_create = {}

        with open(reviews_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # words to censor in reviews

            words_to_censor = load_json_data(
                os.path.join(settings.BASE_DIR,
                             'game\\censor_data.json')
            )

            for row in reader:
                movie_ref = row['Movie']
                norm_title = normalize_title(movie_ref)

                rating_str = row['Rating']
                stars = rating_str.count('★')

                # Jeśli to recenzja bez gwiazdek
                if stars == 0 and '½' not in rating_str:
                    continue

                review_text = row['Review'].strip()

                if norm_title in movies_info:
                    if norm_title not in movies_to_create:
                        movies_to_create[norm_title] = {
                            'real_title': movies_info[norm_title][
                                'real_title'
                            ],
                            'poster': movies_info[norm_title]['poster'],
                            'rev1': None,
                            'rev3': None,
                            'rev5': None
                        }

                    # Przypisywanie recenzji na podstawie gwiazdek
                    entry = movies_to_create[norm_title]
                    if stars <= 2 and not entry['rev1']:
                        entry['rev1'] = censor_review(
                            review_text,
                            movies_info[norm_title]['real_title'],
                            words_to_censor
                            )
                    elif stars == 3 and not entry['rev3']:
                        entry['rev3'] = censor_review(
                            review_text,
                            movies_info[norm_title]['real_title'],
                            words_to_censor
                            )
                    elif stars >= 4 and not entry['rev5']:
                        entry['rev5'] = censor_review(
                            review_text,
                            movies_info[norm_title]['real_title'],
                            words_to_censor
                            )

        self.stdout.write("4. Saving to database")
        saved_count = 0

        for data in movies_to_create.values():
            if data['rev1'] and data['rev3'] and data['rev5']:
                movie, created = Movie.objects.get_or_create(
                    title=data['real_title'],
                    defaults={
                        'poster_url': data['poster'],
                        'review_1': data['rev1'],
                        'review_3': data['rev3'],
                        'review_5': data['rev5']
                    }
                )

                if created:
                    saved_count += 1
                    success_msg = f"Added: {data['real_title']}"
                    self.stdout.write(self.style.SUCCESS(success_msg))

                if saved_count >= 50:
                    break

        final_msg = f"\nSuccess, added: {saved_count} complete movies."
        self.stdout.write(self.style.SUCCESS(final_msg))
