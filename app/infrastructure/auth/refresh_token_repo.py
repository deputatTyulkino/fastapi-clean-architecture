from typing import cast

from redis.asyncio import Redis

from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo


class RefreshTokenRepo(IRefreshTokenRepo):
    def __init__(self, state_client: Redis, ttl: int):
        self.state_client = state_client
        self.ttl = ttl

    def _token_key(self, token_hash: str) -> str:
        return f"refresh:{token_hash}"

    def _family_key(self, family_id: str) -> str:
        return f"refresh_family:{family_id}"

    async def create(self, token_hash: str, user_id: int, family_id: str) -> None:
        async with self.state_client.pipeline(transaction=True) as p:
            token_key = self._token_key(token_hash)
            family_key = self._family_key(family_id)
            await p.hset(
                token_key, mapping={"user_id": user_id, "family_id": family_id}
            )
            await p.hexpire(token_key, self.ttl)
            await p.sadd(family_key, token_hash)
            await p.expire(family_key, self.ttl)
            await p.execute()

    async def get(self, token_hash: str) -> dict | None:
        data = await self.state_client.hgetall(self._token_key(token_hash))
        if data is None:
            return None
        return {"user_id": int(data["user_id"]), "family_id": data["family_id"]}

    async def rotate(
        self, old_token_hash: str, new_token_hash: str, user_id: int, family_id: str
    ) -> None:
        async with self.state_client.pipeline(transaction=True) as p:
            await p.delete(self._token_key(old_token_hash))
            await p.srem(self._family_key(family_id), old_token_hash)
            token_key = self._token_key(new_token_hash)
            family_key = self._family_key(family_id)
            await p.hset(
                token_key, mapping={"user_id": user_id, "family_id": family_id}
            )
            await p.hexpire(token_key, self.ttl)
            await p.sadd(family_key, new_token_hash)
            await p.expire(family_key, self.ttl)
            await p.execute()

    async def revoke_family(self, family_id: str) -> None:
        token_hashes = await self.state_client.smembers(self._family_key(family_id))
        async with self.state_client.pipeline(transaction=True) as p:
            for token_hash in token_hashes:
                await p.delete(self._token_key(cast(str, token_hash)))
            await p.delete(self._family_key(family_id))
            await p.execute()
