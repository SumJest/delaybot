from typing import Type, Optional

from sqlalchemy.future import select

from database.connection import async_session_maker


class BaseDAO:
    model = None  # Модель будет задаваться в наследниках

    @classmethod
    async def create(cls, **kwargs):
        """Создать запись."""
        async with async_session_maker() as session:
            instance = cls.model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            session.close()
            return instance

    @classmethod
    async def get(cls, id: int) -> Optional[Type[model]]:
        """Получить запись по ID."""
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).filter(cls.model.id == id))
            return result.scalars().first()

    @classmethod
    async def update(cls, id: int, **kwargs) -> Optional[Type[model]]:
        """Обновить запись."""
        async with async_session_maker() as session:
            instance = await cls.get(id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                await session.refresh(instance)
            return instance

    @classmethod
    async def delete(cls, id: int) -> bool:
        """Удалить запись."""
        async with async_session_maker() as session:
            instance = await cls.get(id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
