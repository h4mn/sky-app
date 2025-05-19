import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.discord_service import DiscordService, PaginacaoView

@pytest.mark.asyncio
async def test_fluxo_integracao_completo(monkeypatch):
    mock_logger = MagicMock()
    service = DiscordService(logger=mock_logger)
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    mensagem = MagicMock()
    mensagem.content = "Texto para traduzir"

    # Mock das dependências externas
    with patch("app.infra.discord_service.TokenizadorTexto.contar_tokens", return_value=10), \
         patch("app.infra.discord_service.FabricaTraducao.criar_estrategia") as mock_fabrica, \
         patch("app.infra.discord_service.GerenciadorArquivos.salvar_traducao", return_value="/tmp/arquivo.txt"):
        mock_estrategia = MagicMock()
        mock_estrategia.traduzir = AsyncMock(return_value=("Texto traduzido", {"metricas": 1}))
        mock_fabrica.return_value = mock_estrategia
        await service._executar_traducao_adaptativa(interaction, mensagem)
        interaction.followup.send.assert_called()

    # Teste de paginação
    ctx = MagicMock()
    ctx.send = AsyncMock()
    conteudo = ["Página 1", "Página 2", "Página 3"]
    await service.paginar(ctx, conteudo, titulo="Fluxo Integração")
    ctx.send.assert_called()

    # Teste de tratamento de erro
    erro = Exception("Erro simulado no fluxo")
    await service._tratar_erro(interaction, erro, "Erro ao executar fluxo de integração")
    interaction.followup.send.assert_called()