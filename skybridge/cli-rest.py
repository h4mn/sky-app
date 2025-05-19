import os
import requests
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RestClient:
    def __init__(self, env_file: str = 'cli-rest.env'):
        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv(env_file)
        
        # Inicializa as configurações da API
        self.api_url = os.getenv('API_URL')
        self.api_token = os.getenv('API_TOKEN')
        
        if not self.api_url or not self.api_token:
            raise ValueError('API_URL e API_TOKEN devem ser definidos no arquivo .env')
        
        # Configura os headers padrão
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Realiza uma requisição HTTP para a API."""
        url = f'{self.api_url}/{endpoint.lstrip("/")}'
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data if data else None,
                verify=True  # Habilita verificação SSL
            )
            
            # Registra a requisição
            logger.info(f'{method} {url} - Status: {response.status_code}')
            
            # Verifica se a resposta foi bem-sucedida
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Erro na requisição: {str(e)}')
            raise
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Realiza uma requisição GET."""
        return self._make_request('GET', endpoint)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza uma requisição POST."""
        return self._make_request('POST', endpoint, data)
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza uma requisição PUT."""
        return self._make_request('PUT', endpoint, data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Realiza uma requisição DELETE."""
        return self._make_request('DELETE', endpoint)



def main():
    import sys
    import json
    
    # Verifica se há argumentos suficientes
    if len(sys.argv) < 2:
        print('Uso: python cli-rest.py <ENDPOINT> [GET|POST|PUT|DELETE] [DADOS_JSON]')
        print('  - ENDPOINT: Caminho do endpoint (obrigatório)')
        print('  - GET|POST|PUT|DELETE: Método HTTP (opcional, padrão: GET)')
        print('  - DADOS_JSON: Dados em formato JSON (opcional para POST/PUT)')
        sys.exit(1)
    
    try:
        # Extrai os argumentos
        command = sys.argv[1].lower()
        
        endpoint = command
        method = sys.argv[2].upper() if len(sys.argv) > 2 else 'GET'
        
        # Valida o método HTTP
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            print(f'Método HTTP inválido: {method}')
            print('Métodos válidos: GET, POST, PUT, DELETE')
            sys.exit(1)
        
        # Processa dados JSON se fornecidos
        data = None
        if len(sys.argv) > 3:
            try:
                data = json.loads(sys.argv[3])
            except json.JSONDecodeError:
                print('Erro: DADOS_JSON inválido. Forneça um JSON válido.')
                sys.exit(1)
        
        # Cria uma instância do cliente REST
        client = RestClient()
        
        # Executa a requisição apropriada
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, data or {})
        elif method == 'PUT':
            response = client.put(endpoint, data or {})
        else:  # DELETE
            response = client.delete(endpoint)
        
        # Exibe a resposta formatada
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f'Erro: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()