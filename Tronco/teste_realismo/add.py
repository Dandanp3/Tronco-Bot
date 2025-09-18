import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CAMINHO_JSON = "teste_realismo/teste.json"
USUARIO_AUTORIZADO = 505806599034765323  

class Questoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="questão_adicionar", description="Adicionar uma nova questão ao teste")
    @app_commands.describe(
        enunciado="Digite o enunciado da questão",
        a="Alternativa A",
        b="Alternativa B",
        c="Alternativa C",
        d="Alternativa D",
        resposta="Letra da resposta correta (a, b, c ou d)"
    )
    async def adicionar(
        self,
        interaction: discord.Interaction,
        enunciado: str,
        a: str,
        b: str,
        c: str,
        d: str,
        resposta: str
    ):
        # Permissão: ADM ou ID específico
        if not interaction.user.guild_permissions.administrator and interaction.user.id != USUARIO_AUTORIZADO:
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        resposta = resposta.lower()
        if resposta not in ["a", "b", "c", "d"]:
            await interaction.response.send_message("A resposta deve ser uma das letras: a, b, c ou d.", ephemeral=True)
            return

        nova_questao = {
            "enunciado": enunciado,
            "alternativas": {
                "a": a,
                "b": b,
                "c": c,
                "d": d
            },
            "resposta": resposta
        }

        # Lê o JSON atual ou cria lista nova
        if os.path.exists(CAMINHO_JSON):
            with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
                dados = json.load(f)
        else:
            dados = []

        dados.append(nova_questao)

        # Salva de volta
        with open(CAMINHO_JSON, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        await interaction.response.send_message("✅ Questão adicionada!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Questoes(bot))
