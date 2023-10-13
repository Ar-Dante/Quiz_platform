import json

from app.db.db import get_redis
from app.utils.repository import RedisDataService


class RedisService(RedisDataService):

    async def store_results(self,
                            quiz_id: int,
                            company_id: int,
                            current_user: int,
                            correct_count: int,
                            total_count: int):
        key = f"quiz_answers:{quiz_id}:{current_user}:{company_id}"
        redis = await get_redis()
        await self.store_data(redis, key, json.dumps({
            "quiz_id": quiz_id,
            "company_id": company_id,
            "user_id": current_user,
            "correct_count": correct_count,
            "total_count": total_count,
        }))
        await redis.close()


redis_service = RedisService()
