from time import sleep
from proj.tasks import mess, parse_html_tags

res = mess.delay()
# sleep(2)
while res.state != 'SUCCESS':
    print('Wait', res.state)
print(type(res.state), res.state)
print(res.get(timeout=1))

res = parse_html_tags.delay('https://google.com')
# sleep(2)
while res.state != 'SUCCESS':
    print('Wait', res.state)
print(type(res.state), res.state)
print(res.get(timeout=1))
