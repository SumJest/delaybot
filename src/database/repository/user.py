from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from database.models import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User
