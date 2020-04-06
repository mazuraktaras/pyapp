from faker import Faker
from random import randint, choice
import requests
from threading import Thread

number_of_users = 2
max_posts_per_user = 20
max_likes_per_user = 20

fake = Faker(['ru_RU', 'en_GB'])


def bot():
    for _ in range(number_of_users):
        username, password = fake.email(), fake.password(length=7, special_chars=False,
                                                         digits=True, upper_case=True,
                                                         lower_case=True)
        payload = {'username': username, 'password': password}
        requests.post('http://127.0.0.1:5000/api/signup', data=payload)
        response = requests.post('http://127.0.0.1:5000/api/login', data=payload)
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        for _ in range(randint(1, max_posts_per_user)):
            post_text = fake.text(max_nb_chars=200, ext_word_list=None)
            payload = {'post_text': post_text}
            response = requests.post('http://127.0.0.1:5000/api/posts', headers=headers, data=payload)
        for _ in range(randint(1, max_likes_per_user)):
            response = requests.get('http://127.0.0.1:5000/api/posts', headers=headers)
            posts = response.json()['posts']
            post_ids = [post['post_id'] for post in posts]

            payload = {'post_id': choice(post_ids), 'like': 1}
            requests.post('http://127.0.0.1:5000/api/rating', headers=headers, data=payload)
        requests.post('http://127.0.0.1:5000/api/logout', headers=headers)


def bot_run():
    bot_thread = Thread(target=bot, daemon=False)
    bot_thread.start()
    print(bot_thread.name)


if __name__ == '__main__':

    bot_run()
    bot_run()

    # del bot_thread
    # bot_thread.start()

    # print(bot_thread.is_alive())

    for i in range(10):
        print(i)
