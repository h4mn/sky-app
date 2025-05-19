import discord
from typing import List, Dict, Any
from ..config import MAX_TAMANHO_EMBED

class GeradoresUI:
    @staticmethod
    def criar_paginas_embed(texto_traduzido: str, metricas: Dict[str, Any]) -> List[discord.Embed]:
        """Cria embeds paginados para o texto traduzido e métricas."""
        blocos_embed = []
        if len(texto_traduzido) > MAX_TAMANHO_EMBED:
            for i in range(0, len(texto_traduzido), MAX_TAMANHO_EMBED):
                trecho = texto_traduzido[i:i+MAX_TAMANHO_EMBED]
                blocos_embed.append(trecho)
        else:
            blocos_embed = [texto_traduzido]
        resumo_metricas = (
            f"**Modelo:** {metricas['modelo_usado']}\n"
            f"**Blocos processados:** {metricas['blocos_processados']}\n"
            f"**Tokens (entrada/saída):** {metricas['tokens_entrada']}/{metricas['tokens_saida']}\n"
            f"**Custo estimado:** ${metricas['custo_estimado']:.6f}"
        )
        paginas = []
        for i, bloco in enumerate(blocos_embed):
            embed = discord.Embed(
                title=f"Tradução ({i+1}/{len(blocos_embed)})",
                description=bloco,
                color=0x3498db
            )
            if i == 0:
                embed.add_field(name="📊 Métricas", value=resumo_metricas, inline=False)
            embed.set_footer(text=f"SkyApp Translation • {len(blocos_embed)} página(s)")
            paginas.append(embed)
        return paginas