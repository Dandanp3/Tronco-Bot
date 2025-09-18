import discord
from discord.ext import commands
import json
import os

# ========== CONFIGURAÇÕES MALIK ==========
MALIK = {
    "id_servidor": 1358352502285926410,
    "historico": "teste_realismo/historico.json"
}

# ========== CONFIGURAÇÕES VALKARIA ==========
VALKARIA = {
    "id_servidor": 1377281011456675920,
    "historico": "teste_realismo/historicoValkaria.json"
}

# ===== Funções utilitárias JSON =====
def carregar_json(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return padrao
    return padrao

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ===== Comando info =====
def setup(bot: commands.Bot):
    @bot.command(name="info")
    async def info(ctx, membro: discord.Member = None):
        membro = membro or ctx.author

        # Define qual histórico usar
        if ctx.guild.id == MALIK["id_servidor"]:
            caminho_historico = MALIK["historico"]
        elif ctx.guild.id == VALKARIA["id_servidor"]:
            caminho_historico = VALKARIA["historico"]
        else:
            await ctx.send("⚠️ Este servidor não está configurado para histórico de testes.")
            return

        historico = carregar_json(caminho_historico, {})
        user_id = str(membro.id)
        testes = historico.get(user_id, [])

        embed = discord.Embed(
            title=f"📊 Histórico de Testes de {membro}",
            color=discord.Color.blue()
        )

        total_testes = len(testes)
        embed.add_field(name="Total de Testes Realizados", value=str(total_testes), inline=False)

        if total_testes == 0:
            embed.description = "Nenhum teste registrado para este usuário."
        else:
            linhas = []
            for i, registro in enumerate(testes, start=1):
                nota = registro.get("nota", "N/A")
                data = registro.get("data", "N/A")
                linhas.append(f"**{i}.** Nota: {nota} - Data: {data}")

            embed.add_field(name="Detalhes:", value="\n".join(linhas), inline=False)

        await ctx.send(embed=embed)
