import discord
from discord.ext import commands
from discord.ui import View, Button
import json
from datetime import datetime, timedelta
import os

# Configuração para múltiplos servidores
CONFIG_SERVERS = {
    1358352502285926410: {  # Malik
        "CAMINHO_TESTE": "teste_realismo/teste.json",
        "CAMINHO_APROVADOS": "teste_realismo/aprovados.json",
        "CAMINHO_TEMPO": "teste_realismo/tempoTeste.json",
        "CAMINHO_HISTORICO": "teste_realismo/historico.json",
        "ID_CHAT_STAFF": 1392274899137204346,
        "ID_CARGO_STRIKE": 1358354470454562940
    },
    1377281011456675920: {  # Valkaria
        "CAMINHO_TESTE": "teste_realismo/testeValkaria.json",
        "CAMINHO_APROVADOS": "teste_realismo/aprovadosValkaria.json",
        "CAMINHO_TEMPO": "teste_realismo/tempoValkaria.json",
        "CAMINHO_HISTORICO": "teste_realismo/historicoValkaria.json",
        "ID_CHAT_STAFF": 1402773458387079238,
        "ID_CARGO_STRIKE": 1402773162151645357
    }
}

# Utilitários JSON
def carregar_json(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return padrao
    return padrao

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# View dinâmica para pergunta
def criar_view_pergunta(usuario_id, alternativas, callback):
    class BotaoAlternativa(Button):
        def __init__(self, letra):
            super().__init__(label=letra.upper(), style=discord.ButtonStyle.primary, custom_id=f"{usuario_id}-{letra}")
            self.letra = letra

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != usuario_id:
                await interaction.response.send_message("❌ Esse botão não é para você.", ephemeral=True)
                return
            await interaction.response.defer()
            await callback(interaction, self.letra)

    class TestePergunta(View):
        def __init__(self):
            super().__init__(timeout=300)
            for letra in alternativas:
                self.add_item(BotaoAlternativa(letra))

        async def on_timeout(self):
            try:
                await self.message.edit(content="⏰ Tempo esgotado.", view=None)
            except:
                pass

    return TestePergunta()

# Função principal do teste
async def iniciar_teste(usuario, bot, config):
    perguntas = carregar_json(config["CAMINHO_TESTE"], [])
    if not perguntas:
        return await usuario.send("Erro: Nenhuma questão encontrada.")

    respostas_usuario = []

    async def proxima(interaction, resposta):
        respostas_usuario.append(resposta)

        if len(respostas_usuario) >= len(perguntas):
            await finalizar_teste(usuario, respostas_usuario, perguntas, bot, config)
            return

        q = perguntas[len(respostas_usuario)]
        embed = discord.Embed(
            title=f"📘 Pergunta {len(respostas_usuario)+1}/{len(perguntas)}",
            description=f"**{q['enunciado']}**",
            color=discord.Color.blue()
        )
        for letra, texto in q['alternativas'].items():
            embed.add_field(name=f":regional_indicator_{letra.lower()}: {letra.upper()}", value=texto, inline=False)

        view = criar_view_pergunta(usuario.id, list(q['alternativas'].keys()), proxima)
        view.message = interaction.message
        await interaction.message.edit(embed=embed, view=view)

    # Primeira pergunta
    q = perguntas[0]
    embed = discord.Embed(
        title="📘 Pergunta 1",
        description=f"**{q['enunciado']}**",
        color=discord.Color.blue()
    )
    for letra, texto in q['alternativas'].items():
        embed.add_field(name=f":regional_indicator_{letra.lower()}: {letra.upper()}", value=texto, inline=False)

    view = criar_view_pergunta(usuario.id, list(q['alternativas'].keys()), proxima)
    view.message = await usuario.send(embed=embed, view=view)

# Finaliza o teste e salva histórico
async def finalizar_teste(usuario, respostas, perguntas, bot, config):
    nota = sum(1 for r, p in zip(respostas, perguntas) if r == p['resposta'])

    historico = carregar_json(config["CAMINHO_HISTORICO"], {})
    registro = {
        "nota": nota,
        "data": datetime.now().strftime('%d/%m/%Y')
    }
    historico.setdefault(str(usuario.id), []).append(registro)
    salvar_json(config["CAMINHO_HISTORICO"], historico)

    if nota >= 14:
        aprovados = carregar_json(config["CAMINHO_APROVADOS"], {})
        aprovados[str(usuario.id)] = {
            "nome": str(usuario),
            "nota": nota,
            "data": datetime.now().isoformat()
        }
        salvar_json(config["CAMINHO_APROVADOS"], aprovados)
    else:
        tempos = carregar_json(config["CAMINHO_TEMPO"], {})
        tempos[str(usuario.id)] = (datetime.now() + timedelta(days=1)).isoformat()
        salvar_json(config["CAMINHO_TEMPO"], tempos)

    canal = bot.get_channel(config["ID_CHAT_STAFF"])
    embed = discord.Embed(
        title=f"📁 Resultado do teste de {usuario.display_name}",
        description=f"Nota: **{nota}**/20",
        color=discord.Color.purple()
    )

    for i, (resp, pergunta) in enumerate(zip(respostas, perguntas), start=1):
        letra_marcada = resp.lower()
        letra_correta = pergunta['resposta'].lower()

        texto_marcado = pergunta['alternativas'].get(letra_marcada, "*Alternativa inválida*")
        texto_correta = pergunta['alternativas'].get(letra_correta, "*Alternativa inválida*")

        correto = '✅' if letra_marcada == letra_correta else '❌'

        embed.add_field(
            name=f"{i}. {pergunta['enunciado']}",
            value=(
                f"Escolheu: **{letra_marcada.upper()}** - {texto_marcado} {correto}\n"
                f"Correta: **{letra_correta.upper()}** - {texto_correta}"
            ),
            inline=False
        )

    await canal.send(embed=embed)
    await usuario.send("📨 Sua prova foi enviada para correção. Aguarde o resultado!")

# Comando solicitar adaptado
def setup(bot):
    @bot.command(name="solicitar", aliases=["Solicitar"])
    async def solicitar(ctx):
        config = CONFIG_SERVERS.get(ctx.guild.id)
        if not config:
            return await ctx.send("⚠️ Este servidor não está configurado para o teste.")

        if any(role.id == config["ID_CARGO_STRIKE"] for role in ctx.author.roles):
            return await ctx.send(f"🚫 {ctx.author.mention}, você está com um STRIKE ativo. Aguarde o fim da punição.")

        tempos = carregar_json(config["CAMINHO_TEMPO"], {})
        agora = datetime.now()

        if str(ctx.author.id) in tempos:
            limite = datetime.fromisoformat(tempos[str(ctx.author.id)])
            if limite > agora:
                restante = limite - agora
                horas, resto = divmod(restante.seconds, 3600)
                minutos = resto // 60
                return await ctx.send(f"⏳ {ctx.author.mention}, aguarde **{horas}h {minutos}m** para tentar novamente.")

        embed = discord.Embed(
            title="📋 Teste de Realismo",
            description="Você está pronto para iniciar o teste? Clique no botão abaixo para começar.",
            color=discord.Color.green()
        )

        class ConfirmarTeste(View):
            def __init__(self):
                super().__init__(timeout=300)
                self.msg_confirmar = None

            async def on_timeout(self):
                if self.msg_confirmar:
                    try:
                        await self.msg_confirmar.delete()
                    except:
                        pass
                await super().on_timeout()

            @discord.ui.button(label="Começar o teste ✅", style=discord.ButtonStyle.success)
            async def iniciar(self, interaction: discord.Interaction, button: Button):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esse botão não é para você.", ephemeral=True)
                if self.msg_confirmar:
                    try:
                        await self.msg_confirmar.delete()
                    except:
                        pass
                await interaction.response.defer()
                await iniciar_teste(ctx.author, bot, config)

        view = ConfirmarTeste()
        view.msg_confirmar = await ctx.author.send(embed=embed, view=view)
        await ctx.send(f"✉️ {ctx.author.mention}, verifique seu privado para começar o teste. Boa sorte!")
