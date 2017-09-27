from collections import namedtuple

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

Film = namedtuple('Film', 'name, rating, votes_count')


def get_films_from_afisha(min_cinemas_count=10):
    afisha_url = 'https://www.afisha.ru/msk/schedule_cinema/'
    responce = requests.get(afisha_url)
    soup = BeautifulSoup(responce.text, 'html.parser')
    all_films = soup.find_all(attrs={'class': 'object s-votes-hover-area collapsed'})
    films = [film.find_all(attrs={'class': 'usetags'})[0].text for film in all_films
             if len(film.find_all(attrs={'class': 'b-td-item'})) >= min_cinemas_count]
    return films


def get_film_rating(film_name):
    kinopoisk_url = 'https://www.kinopoisk.ru/index.php'
    url_params = {'first': 'yes', 'kp_query': film_name}
    responce = requests.get(kinopoisk_url, params=url_params)
    soup = BeautifulSoup(responce.text, 'html.parser')
    rating_tag = soup.find(attrs={'class': 'rating_ball'})
    if rating_tag:
        rating = float(rating_tag.text)
    else:
        rating = 0
    votes_tag = soup.find(attrs={'class': 'ratingCount'})
    if votes_tag:
        votes = int(''.join(votes_tag.text.split()))
    else:
        votes = 0
    return Film._make([film_name, rating, votes])


def output_films_to_console(films, count=10):
    sorted_films = [film for film in sorted(films, key=lambda x: x.rating, reverse=True)]
    print('\n'.join(['Фильм "{}" имеет рейтинг {} при {} голосах'.format(*film) for film in sorted_films[:count]]))


if __name__ == '__main__':
    films_list = get_films_from_afisha()
    films_with_rating = [get_film_rating(film) for film in tqdm(films_list, desc='Collecting data: ')]
    output_films_to_console(films_with_rating)
