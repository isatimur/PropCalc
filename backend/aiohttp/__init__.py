class ClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        pass

    def get(self, *args, **kwargs):
        raise NotImplementedError("aiohttp is not installed")
