from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database.repository.user import UserRepository


class UserService(SQLAlchemyAsyncRepositoryService[UserRepository]):
    repository = UserRepository
