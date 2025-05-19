import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging

from app.infra.discord_service import DiscordService
from app.infra.logger_service import get_logger
from app.config import VIEW_TIMEOUT

# Configuração do logger
logger = get_logger()

# Configuração do cliente Discord
intents = discord.Intents.default()
intents.message_content = True
app = commands.Bot(command_prefix='!', intents=intents)

# Inicialização do serviço
discord_service = DiscordService(logger)

@app.event
async def on_ready():
    logger.info(f'🚀 Bot conectado como {app.user.name}')
    try:
        synced = await app.tree.sync()
        logger.info(f'✅ Sincronizados {len(synced)} comandos')
    except Exception as e:
        logger.error(f'❌ Erro ao sincronizar comandos: {e}')

@app.tree.command(name="traduzir", description="Traduz uma mensagem usando a Sky")
async def traduzir(interaction: discord.Interaction, mensagem_id: str):
    """Comando para traduzir uma mensagem específica pelo ID"""
    try:
        # Tenta obter a mensagem pelo ID
        canal = interaction.channel
        mensagem = await canal.fetch_message(int(mensagem_id))
        await interaction.response.defer(ephemeral=True)
        
        # Usa o serviço para processar a tradução
        await discord_service._executar_traducao_adaptativa(interaction, mensagem)
    except discord.NotFound:
        await interaction.response.send_message("❌ Mensagem não encontrada!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ ID de mensagem inválido!", ephemeral=True)
    except Exception as e:
        logger.error(f"Erro ao traduzir mensagem: {e}")
        await interaction.response.send_message(f"❌ Erro ao traduzir: {str(e)}", ephemeral=True)

@app.tree.context_menu(name="Traduzir com Sky")
async def traduzir_contexto(interaction: discord.Interaction, mensagem: discord.Message):
    """Menu de contexto para traduzir uma mensagem"""
    try:
        await discord_service._executar_traducao_adaptativa(interaction, mensagem)
    except Exception as e:
        logger.error(f"Erro no menu de contexto: {e}")

def iniciar_bot():
    """Função principal para iniciar o bot"""
    # Obter token do ambiente ou arquivo de configuração
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ Token do Discord não encontrado! Configure a variável de ambiente DISCORD_TOKEN.")
        return
    
    try:
        logger.info("🔄 Iniciando o bot SkyApp...")
        app.run(token, log_handler=None)  # log_handler=None para evitar logs duplicados
    except discord.LoginFailure:
        logger.error("❌ Token inválido! Verifique suas credenciais.")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    iniciar_bot()