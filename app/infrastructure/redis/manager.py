import uuid

from redis.asyncio import ConnectionPool, Redis

from app.domain.interfaces.redis.i_redis_manager import IRedisManager, RedisPoolPurpose

_POOL_CONFIG: dict[RedisPoolPurpose, dict] = {
    RedisPoolPurpose.CACHE: {
        "url_attr": "volatile",
        "db": 0,
        "max_connections": 50,
        "socket_timeout": 2.0,
    },
    RedisPoolPurpose.LIMITER: {
        "url_attr": "volatile",
        "db": 1,
        "max_connections": 100,
        "socket_timeout": 1.0,
    },
    RedisPoolPurpose.STATE: {
        "url_attr": "durable",
        "db": 2,
        "max_connections": 20,
        "socket_timeout": 2.0,
    },
}


class RedisManager(IRedisManager):
    _RELEASE_LOCK_LUA = """
          if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
          else
            return 0
          end
      """
    _POP_SET_LUA = """
          local ids = redis.call('SMEMBERS', KEYS[1])
          redis.call('DEL', KEYS[1])
          return ids
      """

    def __init__(self, volatile_url: str, durable_url: str):
        self._urls = {"volatile": volatile_url, "durable": durable_url}
        self._pools: dict[RedisPoolPurpose, ConnectionPool] = {}

    async def init(self) -> None:
        for purpose, config in _POOL_CONFIG.items():
            base_url = f"{self._urls[config['url_attr']]}/{config['db']}"
            self._pools[purpose] = ConnectionPool.from_url(
                url=base_url,
                max_connections=config["max_connections"],
                socket_timeout=config["socket_timeout"],
                decode_responses=True,
            )

    async def close(self) -> None:
        for pool in self._pools.values():
            await pool.disconnect()
        self._pools.clear()

    def _client(self, purpose: RedisPoolPurpose) -> Redis:
        pool = self._pools.get(purpose)
        if pool is None:
            raise RuntimeError("RedisManager не инициализирован. Вызовите await init()")
        return Redis(connection_pool=pool)

    @property
    def cache_client(self) -> Redis:
        return self._client(RedisPoolPurpose.CACHE)

    @property
    def limiter_client(self) -> Redis:
        return self._client(RedisPoolPurpose.LIMITER)

    @property
    def state_client(self) -> Redis:
        return self._client(RedisPoolPurpose.STATE)

    async def acquire_lock(self, key: str, ttl: int) -> str | None:
        token = str(uuid.uuid4())
        acquired = await self.state_client.set(key, token, nx=True, ex=ttl)
        return token if acquired else None

    async def release_lock(self, key: str, token: str) -> None:
        await self.state_client.eval(self._RELEASE_LOCK_LUA, 1, key, token)

    async def mark_product_dirty(self, product_id: int) -> None:
        await self.state_client.sadd("dirty_products", product_id)

    async def pop_dirty_products(self) -> list[int]:
        product_ids = await self.state_client.eval(
            self._POP_SET_LUA, 1, "dirty_products"
        )
        return [int(id) for id in product_ids]
