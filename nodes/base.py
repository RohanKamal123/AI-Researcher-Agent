# nodes/base.py
class BaseNode:
    def __init__(self, name):
        self.name = name

    async def preprocess(self, store):
        pass

    async def execute(self, store):
        raise NotImplementedError

    async def postprocess(self, store):
        pass

    async def run(self, store):
        await self.preprocess(store)
        action = await self.execute(store)
        await self.postprocess(store)
        return action
