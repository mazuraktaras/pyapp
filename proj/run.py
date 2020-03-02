from time import sleep
from proj.tasks import mess

res = mess.delay()
#sleep(2)
while res.state != 'SUCCESS':
    print('Wait', res.state)
print(type(res.state), res.state)
print(res.get(timeout=1))
