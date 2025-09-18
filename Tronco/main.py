import discord
from discord.ext import commands
from teste_realismo import add, solicitar, corrigir, info  

intents = discord.Intents.default()
intents.message_content = True 

class Tronco(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Comando slash de adicionar questão
        await add.setup(self)
        #
        
        solicitar.setup(self)
        corrigir.setup(self)
        info.setup(self)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot conectado como {self.user}")

if __name__ == "__main__":
    bot = Tronco()
    bot.run("TOKEN")
