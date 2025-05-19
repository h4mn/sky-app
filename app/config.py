import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def get_openai_api_key():
        # TODO: Substitua pela forma segura de obter a chave, ex: variável de ambiente
        return os.getenv("OPENAI_API_KEY")

    # Prompts do sistema
    SYSTEM_PROMPT_PTBR = "Você é Sky, uma IA de tradução e apoio ao usuário. Traduza e auxilie conforme solicitado."
    SYSTEM_PROMPT = """
    You are SkyApp, an intelligent bilingual assistant. Your role is to translate between English and Portuguese, preserving tone, meaning, and cultural context. 

    If the message includes links, mentions, emojis, or other non-linguistic elements, focus only on the translatable parts of the message. Do not request clarification unless the entire message is clearly unintelligible.

    If the message contains a mix of languages, identify the main language and translate to the other.

    Your responses must always be translations — do not explain, apologize, or ask questions unless explicitly instructed to.
    """        

# Constantes e configurações centralizadas
MODELOS_CONFIG = {
    "gpt-4.1-nano": {               # Modelo preferencial
        "encoding": "cl100k_base",
        "limite_tokens": 128000,    # Conforme documentação
        "custo_entrada": 0.0010,    # por 1K tokens
        "custo_saida": 0.0020,      # por 1K tokens
    }
}
MODELO_ESCOLHIDO = "gpt-4.1-nano"

# Configurações e constantes globais do projeto SkyApp
MAX_TAMANHO_EMBED = 1800        # Discord tem limite de ~4000 caracteres por embed, 2000 para contas free
LIMITE_TOKENS_PADRAO = 4096     # Exemplo de limite padrão de tokens
VIEW_TIMEOUT = 180              # Timeout padrão para views do Discord (em segundos)

# Adicione outras constantes relevantes aqui