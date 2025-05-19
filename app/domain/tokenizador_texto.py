import tiktoken
from typing import List, Protocol
from app.config import MODELOS_CONFIG, MODELO_ESCOLHIDO

class TokenizadorInterface(Protocol):
    def contar_tokens(self, texto: str, modelo: str = MODELO_ESCOLHIDO) -> int:
        ...
    def fatiar_texto_por_token(self, texto: str, limite: int, modelo: str = MODELO_ESCOLHIDO) -> List[str]:
        ...

class TokenizadorTexto:
    _implementacao: TokenizadorInterface = None

    @classmethod
    def configurar_implementacao(cls, implementacao: TokenizadorInterface):
        cls._implementacao = implementacao

    @staticmethod
    def contar_tokens(texto: str, modelo: str = MODELO_ESCOLHIDO) -> int:
        if TokenizadorTexto._implementacao is None:
            raise RuntimeError("Implementação de Tokenizador não configurada.")
        return TokenizadorTexto._implementacao.contar_tokens(texto, modelo)

    @staticmethod
    def fatiar_texto_por_token(texto: str, limite: int, modelo: str = MODELO_ESCOLHIDO) -> List[str]:
        if TokenizadorTexto._implementacao is None:
            raise RuntimeError("Implementação de Tokenizador não configurada.")
        return TokenizadorTexto._implementacao.fatiar_texto_por_token(texto, limite, modelo)