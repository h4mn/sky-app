from app.domain.estrategia_traducao import GatewayTraducao
from openai import OpenAI
from app.config import Config

class GatewayTraducaoOpenAI(GatewayTraducao):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.get_openai_api_key()
        self.client = OpenAI(api_key=self.api_key)

    async def traduzir(self, texto: str, modelo: str, logger):
        logger.info(f"🔗 Enviando texto para OpenAI: {modelo}")
        try:
            response = self.client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": Config.SYSTEM_PROMPT},
                    {"role": "user", "content": texto}
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            traducao = response.choices[0].message.content.strip()
            logger.info("✅ Tradução recebida da OpenAI")
            return traducao
        except Exception as e:
            logger.error(f"Erro ao traduzir com OpenAI: {e}")
            raise