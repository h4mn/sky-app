from discord import Interaction, Message
from ..application.traduzir_texto import TraduzirTextoUseCase
from ..infra.logger_service import get_logger

class DiscordAdapter:
    def __init__(self, logger=None):
        self.l = logger or get_logger()
        self.traduzir_usecase = TraduzirTextoUseCase(self.l)

    async def traduzir_mensagem(self, interaction: Interaction, mensagem: Message):
        try:
            resultado = await self.traduzir_usecase.executar(mensagem.content)
            if resultado["paginas"] is None:
                await interaction.followup.send(
                    f"🧠 Tradução: {resultado['texto_traduzido']}\n"
                    f"📄 Arquivo salvo em: `{resultado['caminho_arquivo']}`"
                )
            else:
                await interaction.followup.send(
                    content=f"📄 Tradução salva em: `{resultado['caminho_arquivo']}`",
                    embed=resultado["paginas"][0],
                    view=None  # A view de paginação pode ser passada aqui se necessário
                )
        except Exception as e:
            self.l.error(f"❌ Erro ao traduzir! A Sky ficou sem sinal ☁️: {str(e)}")
            await interaction.followup.send(f"❌ Erro ao traduzir! A Sky ficou sem sinal ☁️")