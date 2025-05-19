import tiktoken
from typing import List
from ..domain.tokenizador_texto import TokenizadorInterface
from app.config import MODELOS_CONFIG, MODELO_ESCOLHIDO

class TokenizadorTiktoken(TokenizadorInterface):
    def contar_tokens(self, texto: str, modelo: str = MODELO_ESCOLHIDO) -> int:
        try:
            codificador = tiktoken.get_encoding(MODELOS_CONFIG[modelo]["encoding"])
            return len(codificador.encode(texto))
        except Exception as e:
            raise ValueError(f"Erro ao contar tokens: {e}")

    def fatiar_texto_por_token(self, texto: str, limite: int, modelo: str = MODELO_ESCOLHIDO) -> List[str]:
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