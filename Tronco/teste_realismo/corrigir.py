import discord
from discord.ext import commands
import json
import os

# ========== CONFIGURAÇÕES MALIK ==========
MALIK = {
    "id_servidor": 1358352502285926410,
    "aprovados": "teste_realismo/aprovados.json",
    "cargo_nao_apto": 1366588169436401674,
    "cargo_verificado": 1358354484899745815,
    "chat_geral": 1358354793218703430,
    "chat_aviso": 1366589577447473192
}

# ========== CONFIGURAÇÕES VALKARIA ==========
VALKARIA = {
    "id_servidor": 1377281011456675920,
    "aprovados": "teste_realismo/aprovadosValkaria.json",
    "cargo_nao_apto": 1402773184805208097,
    "cargo_verificado": 1402773183966351520,
    "chat_geral": 1402773542273286184,
    "chat_aviso": 1402773457141366856
}

# ID dono do bot
ID_DONO_BOT = 505806599034765323

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

# ===== Comando corrigir =====
def setup(bot: commands.Bot):
    @bot.command(name="corrigir")
    async def corrigir(ctx: commands.Context):
        print(f"[DEBUG] Comando corrigir chamado por {ctx.author} no servidor {ctx.guild.id}")

        # Verifica permissões
        if not (ctx.author.id == ID_DONO_BOT or ctx.author.guild_permissions.administrator):
            await ctx.send("❌ Apenas administradores ou o dono do bot podem usar este comando.")
            return

        # Determina configuração pelo servidor
        if ctx.guild.id == MALIK["id_servidor"]:
            config = MALIK
        elif ctx.guild.id == VALKARIA["id_servidor"]:
            config = VALKARIA
        else:
            await ctx.send("⚠️ Este servidor não está configurado para correção de testes.")
            return

        aprovados = carregar_json(config["aprovados"], {})
        membros_mencionados = []
        guild = ctx.guild
        canal_aviso = guild.get_channel(config["chat_aviso"])

        # Caso 1: Nenhum aprovado no JSON
        if not aprovados:
            await ctx.send("❌ Nenhum aprovado desta vez.")
            if canal_aviso:
                mensagem = (
                    "📌 **Os testes foram corrigidos!**\n"
                    "Infelizmente, **não houve aprovados**. Todos foram reprovados.\n"
                    "Boa sorte na próxima tentativa!\n\n"
                    "🕕 A próxima correção será amanhã às 18h."
                )
                await canal_aviso.send(mensagem)
            return

        # Caso 2: Promove aprovados
        for uid in list(aprovados.keys()):
            try:
                membro = await guild.fetch_member(int(uid))
                await membro.remove_roles(discord.Object(id=config["cargo_nao_apto"]))
                await membro.add_roles(discord.Object(id=config["cargo_verificado"]))
                membros_mencionados.append(f"<@{uid}>")
            except discord.NotFound:
                print(f"Usuário {uid} não encontrado no servidor {ctx.guild.name}.")
            except discord.Forbidden:
                print(f"Permissão negada ao modificar o usuário {uid}.")
            except Exception as e:
                print(f"Erro ao processar {uid}: {e}")

        salvar_json(config["aprovados"], {})

        if membros_mencionados:
            canal_geral = guild.get_channel(config["chat_geral"])
            lista_aprovados = "\n".join(membros_mencionados)
            mensagem_geral = (
                "🎉 **Parabéns aos aprovados no teste de realismo:**\n"
                f"{lista_aprovados}\n\n"
                "Agora vocês são membros verificados do servidor."
            )
            if canal_geral:
                await canal_geral.send(mensagem_geral)

            await ctx.send("✅ Correção concluída e membros promovidos com sucesso.")

            if canal_aviso:
                mensagem = (
                    "📌 **Os testes foram corrigidos!**\n"
                    "Os aprovados já receberam o cargo de membro verificado.\n"
                    "Boa sorte aos que não passaram.\n\n"
                    f"✅ Total de aprovados: {len(membros_mencionados)}\n"
                    "🕕 A próxima correção será amanhã às 18h."
                )
                await canal_aviso.send(mensagem)
            return

        # Caso 3: JSON tinha aprovados mas nenhum encontrado
        await ctx.send("❌ Nenhum aprovado encontrado no servidor.")
        if canal_aviso:
            mensagem = (
                "📌 **Os testes foram corrigidos!**\n"
                "Infelizmente, **não houve aprovados encontrados no servidor**. Todos foram reprovados.\n"
                "Boa sorte na próxima tentativa!\n\n"
                "🕕 A próxima correção será amanhã às 18h."
            )
            await canal_aviso.send(mensagem)
