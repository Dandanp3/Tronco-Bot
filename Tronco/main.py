import discord
from discord.ext import commands
from teste_realismo import add, solicitar, corrigir, info  

intents = discord.Intents.default()
intents.message_content = True  # Necessário se for usar on_message

class Tronco(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Setup hook chamado - adicione extensões aqui se quiser")

        # Comando slash de adicionar questão
        await add.setup(self)

        # Comando !solicitar
        solicitar.setup(self)

        # Comando !corrigir
        corrigir.setup(self)
        info.setup(self)

        # Sincroniza comandos slash (caso tenha)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot conectado como {self.user}")

if __name__ == "__main__":
    bot = Tronco()
    bot.run("TOKEN")
