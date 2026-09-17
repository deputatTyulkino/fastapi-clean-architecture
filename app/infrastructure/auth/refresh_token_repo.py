from typing import cast

from redis.asyncio import Redis


from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo
from app.domain.interfaces.logging.i_logger import ILogger


class RefreshTokenRepo(IRefreshTokenRepo):
    def __init__(self, state_client: Redis, ttl: int, logger: ILogger):
        self.state_client = state_client
        self.ttl = ttl
        self.logger = logger.bind(repository="RefreshTokenRepo")

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
        self.logger.info("refresh_token_created", user_id=user_id, family_id=family_id)

    async def get(self, token_hash: str) -> dict | None:
        data = await self.state_client.hgetall(self._token_key(token_hash))
        if not data:
            self.logger.debug("refresh_token_not_found")
            return None
        self.logger.debug(
            "refresh_token_found",
            user_id=int(data["user_id"]),
            family_id=data["family_id"],
        )
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
        self.logger.info("refresh_token_rotated", user_id=user_id, family_id=family_id)

    async def revoke_family(self, family_id: str) -> None:
        token_hashes = await self.state_client.smembers(self._family_key(family_id))
        async with self.state_client.pipeline(transaction=True) as p:
            for token_hash in token_hashes:
                await p.delete(self._token_key(cast(str, token_hash)))
            await p.delete(self._family_key(family_id))
            await p.execute()
        self.logger.info(
            "refresh_token_family_revoked",
            family_id=family_id,
            revoked_count=len(token_hashes),
        )
