from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database.models import User
from database.repository.user import UserRepository


class UserService(SQLAlchemyAsyncRepositoryService[User, UserRepository]):
    repository_type = UserRepository
