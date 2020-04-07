from faker import Faker
from random import randint, choice
import requests
from threading import Thread


class BlogBot:

    def __init__(self, number_of_users=None, max_posts_per_user=None, max_likes_per_user=None):
        self.number_of_users = number_of_users
        self.max_posts_per_user = max_posts_per_user
        self.max_likes_per_user = max_likes_per_user
        self.fake = Faker(['ru_RU', 'en_GB'])

    def bot_logic(self):
        for _ in range(self.number_of_users):
            username, password = self.fake.email(), self.fake.password(length=7, special_chars=False,
                                                                       digits=True, upper_case=True,
                                                                       lower_case=True)
            payload = {'username': username, 'password': password}
            requests.post('http://127.0.0.1:5000/api/signup', data=payload)
            response = requests.post('http://127.0.0.1:5000/api/login', data=payload)
            token = response.json()['token']
            headers = {'Authorization': f'Bearer {token}'}
            for _ in range(randint(1, self.max_posts_per_user)):
                post_text = self.fake.text(max_nb_chars=200, ext_word_list=None)
                payload = {'post_text': post_text}
                requests.post('http://127.0.0.1:5000/api/posts', headers=headers, data=payload)
            for _ in range(randint(1, self.max_likes_per_user)):
                response = requests.get('http://127.0.0.1:5000/api/posts', headers=headers)
                posts = response.json()['posts']
                post_ids = [post['post_id'] for post in posts]

                payload = {'post_id': choice(post_ids), 'like': 1}
                requests.post('http://127.0.0.1:5000/api/rating', headers=headers, data=payload)
            requests.post('http://127.0.0.1:5000/api/logout', headers=headers)

    def background_run(self):

        thread = Thread(target=self.bot_logic, daemon=False)
        thread.start()


if __name__ == '__main__':
    bot = BlogBot(number_of_users=2, max_posts_per_user=2, max_likes_per_user=4)

    bot.background_run()
