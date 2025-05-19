import unittest
import unittest.mock as mock
import discord
from discord.ext import commands

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot import iniciar_bot, app

class TestBot(unittest.TestCase):
    @mock.patch('app.discord_adapter')
    async def test_comando_traduzir_sucesso(self, mock_adapter):
        interaction = mock.AsyncMock()
        interaction.channel = mock.AsyncMock()
        interaction.channel.fetch_message = mock.AsyncMock(return_value=mock.MagicMock())
        
        await app.tree.commands[0].callback(interaction, "123")
        
        interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_adapter.traduzir_mensagem.assert_called_once()
    
    @mock.patch('app.discord_adapter')
    async def test_comando_traduzir_mensagem_nao_encontrada(self, mock_adapter):
        interaction = mock.AsyncMock()
        interaction.channel = mock.AsyncMock()
        interaction.channel.fetch_message = mock.AsyncMock(side_effect=discord.NotFound)
        
        await app.tree.commands[0].callback(interaction, "123")
        
        interaction.response.send_message.assert_called_with(
            "❌ Mensagem não encontrada!", ephemeral=True)
    
    @mock.patch('app.discord_adapter')
    async def test_comando_traduzir_id_invalido(self, mock_adapter):
        interaction = mock.AsyncMock()
        interaction.channel = mock.AsyncMock()
        interaction.channel.fetch_message = mock.AsyncMock(side_effect=ValueError)
        
        await app.tree.commands[0].callback(interaction, "abc")
        
        interaction.response.send_message.assert_called_with(
            "❌ ID de mensagem inválido!", ephemeral=True)

if __name__ == "__main__":
    unittest.main()