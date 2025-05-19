import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View
from typing import List, Any
from ..domain.tokenizador_texto import TokenizadorTexto
from ..domain.fabrica_traducao import FabricaTraducao
from ..infra.gerenciador_arquivos import GerenciadorArquivos
from ..config import Config
from ..config import LIMITE_TOKENS_PADRAO, VIEW_TIMEOUT
from .logger_service import get_logger
from .tokenizador_tiktoken import TokenizadorTiktoken
from .geradores_ui import GeradoresUI
from ..adapters.discord_adapter import DiscordAdapter

class PaginacaoView(View):
    def __init__(self, pages):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.pages = pages
        self.current_page = 0

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="⏳ O tempo para interação expirou. Por favor, tente novamente.", view=self)

    @discord.ui.button(label='Anterior', style=discord.ButtonStyle.primary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='Próximo', style=discord.ButtonStyle.primary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
        else:
            await interaction.response.defer()

class DiscordService:
    def __init__(self, logger=None):
        self.l = logger or get_logger()
        TokenizadorTexto.configurar_implementacao(TokenizadorTiktoken())
        intents = discord.Intents.default()
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self._registrar_comandos()
        self.discord_adapter = DiscordAdapter(self.l)

    def _registrar_comandos(self):
        @app_commands.context_menu(name="Traduzir com Sky")
        async def traduzir_context_menu(interaction: discord.Interaction, mensagem: discord.Message):
            await self.discord_adapter.traduzir_mensagem(interaction, mensagem)
        self.bot.tree.add_command(traduzir_context_menu)

    async def _executar_traducao_adaptativa(self, interaction: discord.Interaction, mensagem: discord.Message):
        self.l.info("🔄 [I] Iniciando tradução com Sky...")
        await interaction.response.defer(ephemeral=True)
        # Este método agora é delegado ao adaptador/caso de uso
        try:
            await self.discord_adapter.traduzir_mensagem(interaction, mensagem)
            
            num_tokens = TokenizadorTexto.contar_tokens(mensagem.content)
            self.l.info(f"📊 Mensagem com {num_tokens} tokens")
            estrategia = FabricaTraducao.criar_estrategia(num_tokens)
            texto_traduzido, metricas = await estrategia.traduzir(mensagem.content, self.l)
            caminho_arquivo = GerenciadorArquivos.salvar_traducao(
                mensagem.content,
                texto_traduzido,
                metricas,
                self.l
            )
            if num_tokens < LIMITE_TOKENS_PADRAO:
                await interaction.followup.send(
                    f"🧠 Tradução: {texto_traduzido}\n"
                    f"📄 Arquivo salvo em: `{caminho_arquivo}`"
                )
                return
            paginas = GeradoresUI.criar_paginas_embed(texto_traduzido, metricas)
            view = PaginacaoView(paginas)
            await interaction.followup.send(
                content=f"📄 Tradução salva em: `{caminho_arquivo}`",
                embed=paginas[0],
                view=view
            )
        except Exception as e:
            await self._tratar_erro(interaction, e, "Erro ao traduzir")

    async def _tratar_erro(self, interaction: discord.Interaction, erro: Exception, mensagem_base: str):
        self.l.error(f"❌ {mensagem_base}: {erro}")
        try:
            await interaction.followup.send(f"❌ {mensagem_base}! A Sky ficou sem sinal ☁️")
        except discord.InteractionResponded:
            self.l.warning("⚠️ Resposta já enviada, não foi possível enviar mensagem de erro.")

    async def paginar(self, ctx, conteudo: List[str], titulo: str = "Página"):
        paginas = []
        for i, texto in enumerate(conteudo):
            embed = discord.Embed(
                title=f"{titulo} {i+1}/{len(conteudo)}",
                description=texto,
                color=0x3498db
            )
            embed.set_footer(text=f"SkyApp • {len(conteudo)} página(s)")
            paginas.append(embed)
        view = PaginacaoView(paginas)
        await ctx.send(embed=paginas[0], view=view)

    async def run(self, token: str):
        @self.bot.event
        async def on_ready():
            await self.bot.tree.sync()
            self.l.info(f'✅ DiscordService pronto como {self.bot.user}!')
        await self.bot.start(token)

    async def shutdown(self):
        self.l.info("🔻 Desligando o DiscordService...")
        await self.bot.close()