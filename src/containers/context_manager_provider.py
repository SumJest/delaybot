from dependency_injector import providers


class AsyncContextManager(providers.Provider):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    async def _provide(self, *args, **kwargs):
        # Используем контекстный менеджер для управления сессией
        async with self.manager() as session:
            yield session
