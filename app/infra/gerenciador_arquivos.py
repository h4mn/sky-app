import os
from datetime import datetime

class GerenciadorArquivos:
    @staticmethod
    def gerar_nome_arquivo() -> str:
        """Gera nome de arquivo no formato YYYY.MM.DD.HH.mm.md"""
        return datetime.now().strftime("%Y.%m.%d.%H.%M") + ".md"

    @staticmethod
    def salvar_traducao(texto_original: str, texto_traduzido: str, metricas: dict, logger) -> str:
        """Salva a tradução em arquivo markdown e retorna o caminho"""
        try:
            dir_path = os.path.join("docs", "translations")
            os.makedirs(dir_path, exist_ok=True)
            nome_arquivo = GerenciadorArquivos.gerar_nome_arquivo()
            caminho_completo = os.path.join(dir_path, nome_arquivo)
            conteudo = (
                f"# Tradução - {nome_arquivo}\n\n"
                f"## Texto Original\n{texto_original}\n\n"
                f"## Texto Traduzido\n{texto_traduzido}\n\n"
                f"## Métricas\n"
                f"- Modelo: {metricas['modelo_usado']}\n"
                f"- Tokens (entrada/saída): {metricas['tokens_entrada']}/{metricas['tokens_saida']}\n"
                f"- Custo estimado: ${metricas['custo_estimado']:.6f}\n"
            )
            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            logger.info(f"📄 Tradução salva em: {caminho_completo}")
            return caminho_completo
        except Exception as e:
            logger.error(f"❌ Erro ao salvar tradução: {e}")
            raise