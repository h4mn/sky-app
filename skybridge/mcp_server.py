# Servidor MCP para SkyBridge API
from mcp.server.fastmcp import FastMCP, Context
import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Carrega as variáveis de ambiente
load_dotenv('cli-rest.env')

# Configurações da API
API_URL = os.getenv('API_URL')
API_TOKEN = os.getenv('API_TOKEN')

# Verifica se as configurações estão disponíveis
if not API_URL or not API_TOKEN:
    raise ValueError('API_URL e API_TOKEN devem ser definidos no arquivo cli-rest.env')

# Configura os headers padrão
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Cria um servidor MCP
mcp = FastMCP("SkyBridge API")

# Função auxiliar para fazer requisições à API SkyBridge
def make_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Realiza uma requisição HTTP para a API SkyBridge."""
    url = f'{API_URL}/{endpoint.lstrip("/")}'
    
    response = requests.request(
        method=method,
        url=url,
        headers=HEADERS,
        json=data if data else None,
        verify=True
    )
    
    # Verifica se a resposta foi bem-sucedida
    response.raise_for_status()
    
    return response.json()

# Recursos MCP (equivalentes a GET endpoints)
@mcp.resource("configs://")
def get_configs() -> str:
    """Obtém as configurações disponíveis da API SkyBridge."""
    try:
        configs = make_request('GET', '/configs')
        return json.dumps(configs, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao obter configurações: {str(e)}"

@mcp.resource("status://")
def get_status() -> str:
    """Obtém o status atual da API SkyBridge."""
    try:
        status = make_request('GET', '/status')
        return json.dumps(status, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao obter status: {str(e)}"

# Ferramentas MCP (equivalentes a POST/PUT/DELETE endpoints)
@mcp.tool()
def consultar_endpoint(endpoint: str, metodo: str = "GET", dados: Optional[Dict] = None) -> str:
    """Consulta um endpoint específico da API SkyBridge.
    
    Args:
        endpoint: O caminho do endpoint a ser consultado.
        metodo: O método HTTP a ser utilizado (GET, POST, PUT, DELETE).
        dados: Dados em formato JSON para enviar (opcional para POST/PUT).
    
    Returns:
        A resposta da API em formato JSON.
    """
    try:
        response = make_request(metodo, endpoint, dados)
        return json.dumps(response, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao consultar endpoint {endpoint}: {str(e)}"

@mcp.tool()
def enviar_comando(comando: str, parametros: Optional[Dict] = None) -> str:
    """Envia um comando para a API SkyBridge.
    
    Args:
        comando: O comando a ser enviado.
        parametros: Parâmetros do comando (opcional).
    
    Returns:
        A resposta da API em formato JSON.
    """
    try:
        endpoint = f"/comando/{comando}"
        response = make_request('POST', endpoint, parametros)
        return json.dumps(response, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao enviar comando {comando}: {str(e)}"

# Ponto de entrada para execução direta
if __name__ == "__main__":
    print("Iniciando servidor MCP para SkyBridge API...")
    print(f"API URL: {API_URL}")
    print("Use 'mcp dev mcp_server.py' para testar o servidor com o MCP Inspector")
    print("Ou 'mcp install mcp_server.py' para instalar no Claude Desktop")