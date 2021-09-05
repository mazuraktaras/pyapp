# ----- App configuration section -----
SECRET_KEY = '222bmnkvsk777'
SQLALCHEMY_DATABASE_URI = 'sqlite:///jwtblog.db'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:12345677@ec2-13-53-78-95.eu-north-1.compute.amazonaws.com:3306/blog'
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = '777kjnpsj222'
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access']
JWT_TOKEN_LOCATION = ['headers', 'cookies', 'json']
JWT_COOKIE_CSRF_PROTECT = False
JWT_CSRF_CHECK_FORM = False
JWT_ACCESS_TOKEN_EXPIRES = 3600
PROPAGATE_EXCEPTIONS = True

# ----- Blog Bot configuration section -----
BOT_NUMBER_OF_USERS = 1
BOT_MAX_POSTS_PER_USER = 1
BOT_MAX_LIKES_PER_USER = 1
