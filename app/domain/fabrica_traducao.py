from .estrategia_traducao import EstrategiaTraducao, TraducaoSimples
from app.config import MODELO_ESCOLHIDO
from app.infra.gateway_traducao_openai import GatewayTraducaoOpenAI

class FabricaTraducao:
    @staticmethod
    def criar_estrategia(tamanho_texto: int, modelo_texto: str = MODELO_ESCOLHIDO) -> EstrategiaTraducao:
        """Cria a estratégia adequada com base no tamanho do texto"""
        # Sempre usa o modelo escolhido, independente do tamanho
        return TraducaoSimples(modelo=MODELO_ESCOLHIDO)

    def criar_estrategia(num_tokens: int):
        gateway = GatewayTraducaoOpenAI()
        return TraducaoSimples(gateway=gateway)