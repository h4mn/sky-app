import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View
from openai import OpenAI
import tiktoken
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import asyncio

from config import Config

# Constantes e configurações centralizadas
MODELOS_CONFIG = {
    "gpt-4.1-nano": {  # Modelo preferencial
        "encoding": "cl100k_base",
        "limite_tokens": 128000,  # Conforme documentação
        "custo_entrada": 0.0010,  # por 1K tokens
        "custo_saida": 0.0020,   # por 1K tokens
    }
}

MODELO_ESCOLHIDO = "gpt-4.1-nano"

MAX_TAMANHO_EMBED = 1800  # Discord tem limite de ~4000 caracteres por embed, 2000 para contas free
LIMITE_TOKENS_PADRAO = 4096  # Exemplo de limite padrão de tokens
VIEW_TIMEOUT = 180           # Timeout padrão para views do Discord (em segundos)
SYSTEM_PROMPT = "Você é Sky, uma IA de tradução e apoio ao usuário. Traduza e auxilie conforme solicitado."

# Classe utilitária para manipulação de arquivos
class GerenciadorArquivos:
    @staticmethod
    def gerar_nome_arquivo() -> str:
        """Gera nome de arquivo no formato YYYY.MM.DD.HH.mm.md"""
        from datetime import datetime
        return datetime.now().strftime("%Y.%m.%d.%H.%M") + ".md"

    @staticmethod
    def salvar_traducao(texto_original: str, texto_traduzido: str, metricas: dict, logger) -> str:
        """Salva a tradução em arquivo markdown e retorna o caminho"""
        import os
        try:
            # Cria diretório se não existir
            dir_path = os.path.join("docs", "translations")
            os.makedirs(dir_path, exist_ok=True)
            
            # Gera caminho completo do arquivo
            nome_arquivo = GerenciadorArquivos.gerar_nome_arquivo()
            caminho_completo = os.path.join(dir_path, nome_arquivo)
            
            # Conteúdo do arquivo
            conteudo = (
                f"# Tradução - {nome_arquivo}\n\n"
                f"## Texto Original\n{texto_original}\n\n"
                f"## Texto Traduzido\n{texto_traduzido}\n\n"
                f"## Métricas\n"
                f"- Modelo: {metricas['modelo_usado']}\n"
                f"- Tokens (entrada/saída): {metricas['tokens_entrada']}/{metricas['tokens_saida']}\n"
                f"- Custo estimado: ${metricas['custo_estimado']:.6f}\n"
            )
            
            # Salva arquivo
            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            
            logger.info(f"📄 Tradução salva em: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar tradução: {e}")
            raise

# Classe utilitária para tokens
class TokenizadorTexto:
    @staticmethod
    def contar_tokens(texto: str, modelo: str = MODELO_ESCOLHIDO) -> int:
        """Conta o número de tokens em um texto para um modelo específico."""
        try:
            codificador = tiktoken.get_encoding(MODELOS_CONFIG[modelo]["encoding"])
            return len(codificador.encode(texto))
        except Exception as e:
            raise ValueError(f"Erro ao contar tokens: {e}")

    @staticmethod
    def fatiar_texto_por_token(texto: str, limite: int, modelo: str = MODELO_ESCOLHIDO) -> List[str]:
        """Divide o texto em blocos respeitando o limite de tokens."""
        try:
            codificador = tiktoken.get_encoding(MODELOS_CONFIG[modelo]["encoding"])
            tokens = codificador.encode(texto)

            blocos = []
            for i in range(0, len(tokens), limite):
                bloco_tokens = tokens[i:i + limite]
                blocos.append(codificador.decode(bloco_tokens))

            return blocos
        except Exception as e:
            raise ValueError(f"Erro ao fatiar texto: {e}")

# Classe para geração de componentes visuais do Discord
class GeradoresUI:
    @staticmethod
    def criar_paginas_embed(texto_traduzido: str, metricas: Dict[str, Any]) -> List[discord.Embed]:
        """Cria embeds paginados para o texto traduzido e métricas."""
        # Separa o texto em blocos adequados para embeds do Discord
        blocos_embed = []
        
        # Se o texto é muito grande, cria uma paginação por caracteres
        if len(texto_traduzido) > MAX_TAMANHO_EMBED:
            for i in range(0, len(texto_traduzido), MAX_TAMANHO_EMBED):
                trecho = texto_traduzido[i:i+MAX_TAMANHO_EMBED]
                blocos_embed.append(trecho)
        else:
            blocos_embed = [texto_traduzido]
            
        # Cria resumo das métricas de tradução
        resumo_metricas = (
            f"**Modelo:** {metricas['modelo_usado']}\n"
            f"**Blocos processados:** {metricas['blocos_processados']}\n"
            f"**Tokens (entrada/saída):** {metricas['tokens_entrada']}/{metricas['tokens_saida']}\n"
            f"**Custo estimado:** ${metricas['custo_estimado']:.6f}"
        )
            
        # Cria os embeds paginados
        paginas = []
        for i, bloco in enumerate(blocos_embed):
            embed = discord.Embed(
                title=f"Tradução ({i+1}/{len(blocos_embed)})",
                description=bloco,
                color=0x3498db
            )
            
            # Adiciona as métricas apenas na primeira página
            if i == 0:
                embed.add_field(name="📊 Métricas", value=resumo_metricas, inline=False)
                
            embed.set_footer(text=f"SkyApp Translation • {len(blocos_embed)} página(s)")
            paginas.append(embed)
            
        return paginas

# Interface para estratégias de tradução
class EstrategiaTraducao(ABC):
    @abstractmethod
    async def traduzir(self, texto: str, logger) -> Tuple[str, Dict[str, Any]]:
        """Método abstrato para implementar tradução com diferentes estratégias"""
        pass

# Implementação de estratégia de tradução simples
class TraducaoSimples(EstrategiaTraducao):
    def __init__(self, modelo: str = MODELO_ESCOLHIDO):
        self.modelo = modelo
        
    async def traduzir(self, texto: str, logger) -> Tuple[str, Dict[str, Any]]:
        """Implementa tradução simples para textos pequenos"""
        logger.info(f"🔄 Traduzindo texto simples com {self.modelo}")
        
        client = OpenAI(api_key=Config.GPT.OPENAPI_KEY)
        
        # Contagem de tokens para métricas
        encoding = MODELOS_CONFIG[self.modelo]["encoding"]
        tokens_entrada = TokenizadorTexto.contar_tokens(texto, self.modelo)
        
        try:
            completion = client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": texto}
                ],
                timeout=TIMEOUT_API,
            )
            
            texto_traduzido = completion.choices[0].message.content.strip()
            tokens_saida = TokenizadorTexto.contar_tokens(texto_traduzido, self.modelo)
            
            # Métricas
            logger.info(f"📊 Tradução: {tokens_entrada} tokens entrada, {tokens_saida} tokens saída")
            
            metricas = {
                "modelo_usado": self.modelo,
                "blocos_processados": 1,
                "tokens_entrada": tokens_entrada,
                "tokens_saida": tokens_saida,
                "custo_estimado": EstimadorCusto.calcular(self.modelo, tokens_entrada, tokens_saida)
            }
            
            return texto_traduzido, metricas
            
        except Exception as e:
            logger.error(f"❌ Erro ao traduzir com {self.modelo}: {e}")
            raise

# Fábrica de estratégias de tradução
class FabricaTraducao:
    @staticmethod
    def criar_estrategia(tamanho_texto: int, modelo_texto: str = MODELO_ESCOLHIDO) -> EstrategiaTraducao:
        """Cria a estratégia adequada com base no tamanho do texto"""
        # Sempre usa o modelo escolhido, independente do tamanho
        return TraducaoSimples(modelo=MODELO_ESCOLHIDO)

# Classe utilitária para estimativa de custos
class EstimadorCusto:
    @staticmethod
    def calcular(modelo: str, tokens_entrada: int, tokens_saida: int) -> float:
        """Estima o custo da tradução baseado no modelo e tokens utilizados"""
        try:
            config = MODELOS_CONFIG.get(modelo, {})
            custo_entrada = config.get("custo_entrada", 0)
            custo_saida = config.get("custo_saida", 0)
            
            return (tokens_entrada/1000 * custo_entrada) + (tokens_saida/1000 * custo_saida)
        except Exception:
            return 0

# Sistema de Paginação
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

# Prompts do sistema
SYSTEM_PROMPT = """
You are SkyApp, an intelligent bilingual assistant. Your role is to translate between English and Portuguese, preserving tone, meaning, and cultural context. 

If the message includes links, mentions, emojis, or other non-linguistic elements, focus only on the translatable parts of the message. Do not request clarification unless the entire message is clearly unintelligible.

If the message contains a mix of languages, identify the main language and translate to the other.

Your responses must always be translations — do not explain, apologize, or ask questions unless explicitly instructed to.
"""

# Classe principal do serviço
class SkyAppContextService:
    def __init__(self, logger):
        self.l = logger
        intents = discord.Intents.default()
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self._registrar_comandos()

    def _registrar_comandos(self):
        """Registra os comandos do bot"""
        @app_commands.context_menu(name="Traduzir com Sky")
        async def traduzir_context_menu(interaction: discord.Interaction, mensagem: discord.Message):
            await self._executar_traducao_adaptativa(interaction, mensagem)
            
        self.bot.tree.add_command(traduzir_context_menu)
    
    async def _executar_traducao_adaptativa(self, interaction: discord.Interaction, mensagem: discord.Message):
        """Gerencia o fluxo de tradução adaptativa com base no tamanho do texto"""
        try:
            self.l.info("🔄 Iniciando tradução com Sky...")
            await interaction.response.defer(ephemeral=True)
            
            # Verifica o tamanho do texto
            num_tokens = TokenizadorTexto.contar_tokens(mensagem.content)
            self.l.info(f"📊 Mensagem com {num_tokens} tokens")
            
            # Cria estratégia adequada
            estrategia = FabricaTraducao.criar_estrategia(num_tokens)
            texto_traduzido, metricas = await estrategia.traduzir(mensagem.content, self.l)
            
            # Salva a tradução em arquivo
            caminho_arquivo = GerenciadorArquivos.salvar_traducao(
                mensagem.content,
                texto_traduzido,
                metricas,
                self.l
            )
            
            # Se for texto pequeno e tradução simples, envia mensagem com link para arquivo
            if num_tokens < LIMITE_TOKENS_PADRAO:
                await interaction.followup.send(
                    f"🧠 Tradução: {texto_traduzido}\n"
                    f"📄 Arquivo salvo em: `{caminho_arquivo}`"
                )
                return
                
            # Para textos maiores, usa paginação e informa sobre o arquivo salvo
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
        """Centraliza o tratamento de erros para interações do Discord"""
        self.l.error(f"❌ {mensagem_base}: {erro}")
        try:
            await interaction.followup.send(f"❌ {mensagem_base}! A Sky ficou sem sinal ☁️")
        except discord.InteractionResponded:
            self.l.warning("⚠️ Resposta já enviada, não foi possível enviar mensagem de erro.")
    
    async def paginar(self, ctx, conteudo: List[str], titulo: str = "Página"):
        """Método para paginação genérica de conteúdo"""
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
        """Inicia o bot"""
        @self.bot.event
        async def on_ready():
            await self.bot.tree.sync()
            self.l.info(f'✅ SkyAppContextService pronto como {self.bot.user}!')

        await self.bot.start(token)

    async def shutdown(self):
        """Desliga o bot de forma segura"""
        self.l.info("🔻 Desligando o SkyAppContextService...")
        await self.bot.close()

# Para rodar manualmente:
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SkyApp")
    
    service = SkyAppContextService(logger)
    
    try:
        asyncio.run(service.run(Config.Discord.SKYAPP_TOKEN))
    except KeyboardInterrupt:
        print("Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro ao executar o serviço: {e}")