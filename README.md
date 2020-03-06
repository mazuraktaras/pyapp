# UENERGO counting tags in html document

# Start Celery
celery -A uenergoapp.celapp worker -l info
# Redis in container
docker run -d -p 6379:6379 --name redisserv redis
