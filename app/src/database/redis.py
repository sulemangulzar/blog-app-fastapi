from redis.asyncio import Redis

from app.src.config import settings

_token_blacklist = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def add_jti_to_blacklist(jti: str):
    await _token_blacklist.set(jti, "blacklisted")


async def check_jti_in_blacklist(jti: str) -> bool:
    return bool(await _token_blacklist.exists(jti))
