from proj.tasks import mess

res = mess.delay()

print(res.id, res.state, res.successful(), res.backend)  # , res.get(timeout=1))
print(res.get(timeout=3))
