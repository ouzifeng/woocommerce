import redis

r = redis.Redis(
  host='informed-anchovy-41169.upstash.io',
  port=41169,
  password='39a6f86d4b544454b6653d0dae51320b'
)

r.set('foo', 'bar')
print(r.get('foo'))
