import logging

# Configuração padrão do logger
logger = logging.getLogger("skyapp")
logger.setLevel(logging.INFO)

# Evita adicionar múltiplos handlers em caso de múltiplas importações
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Função utilitária para obter o logger
get_logger = lambda: logger