from app.config import MODELOS_CONFIG

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