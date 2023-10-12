import json

from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS, ERROR_MEMBER_NOT_EXISTS, ERROR_INVALID_SAVE_FORMAT
from app.db.db import get_redis
from app.utils.repository import RedisDataRepository
from app.utils.upload_data import JSONDataLoader, CSVDataLoader


class RedisService(RedisDataRepository):
    json_loader = JSONDataLoader()
    csv_loader = CSVDataLoader()

    async def _save_data(self, data, key, save_format):
        if save_format == "json":
            json_loader = JSONDataLoader()
            json_loader.save(data, str(key) + "-results.json")
        elif save_format == "csv":
            csv_loader = CSVDataLoader()
            csv_loader.save(data, str(key) + "-results.csv")
        else:
            HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_INVALID_SAVE_FORMAT)

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

    async def get_user_results(self, user_id: int, current_user: int, upload_format: str):
        if user_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        redis = await get_redis()
        keys = await redis.keys(f"quiz_answers:*:{user_id}:*")
        results = []

        for key in keys:
            data = await self.get_data(redis, key)
            if data:
                results.append(json.loads(data))
        await self._save_data(results, f"user_id_{user_id}", upload_format)
        await redis.close()
        return results

    async def get_user_results_for_company(self,
                                           user_id: int,
                                           current_user: int,
                                           member: dict,
                                           company: dict,
                                           upload_format: str):
        await self._valid_access(current_user, member, company)
        redis = await get_redis()
        keys = await redis.keys(f"quiz_answers:*:{user_id}:{company.id}")

        results = []
        for key in keys:
            data = await self.get_data(redis, key)
            if data:
                results.append(json.loads(data))

        await redis.close()
        await self._save_data(results, f"user_id_{user_id}_company_id_{company.id}", upload_format)
        return results

    async def get_all_results_for_company(self,
                                          company_id: int,
                                          current_user: int,
                                          member: dict,
                                          company: dict,
                                          upload_format: str):
        await self._valid_access(current_user, member, company)
        redis = await get_redis()
        keys = await redis.keys(f"quiz_answers:*:{company_id}")

        results = []
        for key in keys:
            data = await self.get_data(redis, key)
            if data:
                results.append(json.loads(data))

        await redis.close()
        await self._save_data(results, f"company_id_{company_id}", upload_format)
        return results

    async def get_quiz_results_for_company(self,
                                           quiz_id: int,
                                           current_user: int,
                                           member: dict,
                                           company: dict,
                                           upload_format: str):
        await self._valid_access(current_user, member, company)
        redis = await get_redis()
        keys = await redis.keys(f"quiz_answers:{quiz_id}:*")

        results = []
        for key in keys:
            data = await self.get_data(redis, key)
            if data:
                results.append(json.loads(data))

        await redis.close()
        await self._save_data(results, f"quiz_id_{quiz_id}", upload_format)
        return results

    async def _valid_access(self,
                            current_user: int,
                            member: dict,
                            company: dict):
        if not member and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_EXISTS)
        if company.owner_id != current_user and not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)


redis_service = RedisService()
