from typing import Any, Dict

from discord.enums import try_enum
from ..domain.tokenizador_texto import TokenizadorTexto
from ..domain.fabrica_traducao import FabricaTraducao
from ..infra.gerenciador_arquivos import GerenciadorArquivos
from ..infra.geradores_ui import GeradoresUI
from ..config import LIMITE_TOKENS_PADRAO

class TraduzirTextoUseCase:
    def __init__(self, logger):
        self.l = logger

    async def executar(self, mensagem_content: str) -> Dict[str, Any]:
        self.l.info("🔄 [UC] Iniciando tradução com Sky...")
        try:
            num_tokens = TokenizadorTexto.contar_tokens(mensagem_content)
            self.l.info(f"📊 Mensagem com {num_tokens} tokens")
            estrategia = FabricaTraducao.criar_estrategia(num_tokens)
            texto_traduzido, metricas = await estrategia.traduzir(mensagem_content, self.l)
            caminho_arquivo = GerenciadorArquivos.salvar_traducao(
                mensagem_content,
                texto_traduzido,
                metricas,
                self.l
            )
            if num_tokens < LIMITE_TOKENS_PADRAO:
                return {
                    "texto_traduzido": texto_traduzido,
                    "caminho_arquivo": caminho_arquivo,
                    "paginas": None,
                    "metricas": metricas
                }
            paginas = GeradoresUI.criar_paginas_embed(texto_traduzido, metricas)
            return {
                "texto_traduzido": texto_traduzido,
                "caminho_arquivo": caminho_arquivo,
                "paginas": paginas,
                "metricas": metricas
            }
        except Exception as e:
            self.l.error(f"❌ Erro ao traduzir texto: {str(e)}")
            raise