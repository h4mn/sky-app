import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
import discord
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules["discord"] = discord

from app.infra.discord_service import DiscordService, PaginacaoView

@pytest.mark.asyncio
async def test_traducao_fluxo_basico(monkeypatch):
    mock_logger = MagicMock()
    service = DiscordService(logger=mock_logger)
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    mensagem = MagicMock()
    mensagem.content = "Texto para traduzir"

    with patch("app.infra.discord_service.TokenizadorTexto.contar_tokens", return_value=10), \
         patch("app.infra.discord_service.FabricaTraducao.criar_estrategia") as mock_fabrica, \
         patch("app.infra.discord_service.GerenciadorArquivos.salvar_traducao", return_value="/tmp/arquivo.txt"):
        mock_estrategia = MagicMock()
        mock_estrategia.traduzir = AsyncMock(return_value=("Texto traduzido", {"metricas": 1}))
        mock_fabrica.return_value = mock_estrategia
        await service._executar_traducao_adaptativa(interaction, mensagem)
        interaction.followup.send.assert_called()

@pytest.mark.asyncio
async def test_tratamento_erro(monkeypatch):
    mock_logger = MagicMock()
    service = DiscordService(logger=mock_logger)
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    erro = Exception("Falha de teste")
    await service._tratar_erro(interaction, erro, "Erro ao traduzir")
    interaction.followup.send.assert_called()

@pytest.mark.asyncio
async def test_paginar(monkeypatch):
    mock_logger = MagicMock()
    service = DiscordService(logger=mock_logger)
    ctx = MagicMock()
    ctx.send = AsyncMock()
    conteudo = ["Página 1", "Página 2"]
    await service.paginar(ctx, conteudo, titulo="Teste")
    ctx.send.assert_called()