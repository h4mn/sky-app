from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from app.config import MODELOS_CONFIG, MODELO_ESCOLHIDO
from .tokenizador_texto import TokenizadorTexto
from app.config import Config


class EstrategiaTraducao(ABC):
    @abstractmethod
    async def traduzir(self, texto: str, logger) -> Tuple[str, Dict[str, Any]]:
        """Método abstrato para implementar tradução com diferentes estratégias"""
        pass

class GatewayTraducao(ABC):
    @abstractmethod
    async def traduzir(self, texto: str, modelo: str, logger) -> str:
        pass

class TraducaoSimples(EstrategiaTraducao):
    def __init__(self, modelo: str = MODELO_ESCOLHIDO, gateway: GatewayTraducao = None):
        self.modelo = modelo
        self.gateway = gateway

    async def traduzir(self, texto: str, logger) -> Tuple[str, Dict[str, Any]]:
        logger.info(f"🔄 Traduzindo texto simples com {self.modelo}")
        if not self.gateway:
            raise Exception("Gateway de tradução não fornecido para TraducaoSimples.")
        texto_traduzido = await self.gateway.traduzir(texto, self.modelo, logger)
        tokens_entrada = TokenizadorTexto.contar_tokens(texto, self.modelo)
        tokens_saida = TokenizadorTexto.contar_tokens(texto_traduzido, self.modelo)
        logger.info(f"📊 Tradução: {tokens_entrada} tokens entrada, {tokens_saida} tokens saída")
        from .estimador_custo import EstimadorCusto
        metricas = {
            "modelo_usado": self.modelo,
            "blocos_processados": 1,
            "tokens_entrada": tokens_entrada,
            "tokens_saida": tokens_saida,
            "custo_estimado": EstimadorCusto.calcular(self.modelo, tokens_entrada, tokens_saida)
        }
        return texto_traduzido, metricas