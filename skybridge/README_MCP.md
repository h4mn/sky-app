# Servidor MCP para API SkyBridge

Este projeto implementa um servidor MCP (Model Context Protocol) que expõe as funcionalidades da API SkyBridge para modelos de linguagem como o Claude.

## Requisitos

Certifique-se de ter todas as dependências instaladas:

```bash
pip install -r requirements.txt
```

## Configuração

As configurações da API SkyBridge estão no arquivo `cli-rest.env`. Verifique se as seguintes variáveis estão configuradas corretamente:

- `API_URL`: URL base da API SkyBridge
- `API_TOKEN`: Token de autenticação para a API

## Funcionalidades Expostas

### Recursos (Resources)

- `configs://`: Obtém as configurações disponíveis da API SkyBridge
- `status://`: Obtém o status atual da API SkyBridge

### Ferramentas (Tools)

- `consultar_endpoint`: Consulta um endpoint específico da API SkyBridge
  - Parâmetros: `endpoint`, `metodo` (GET, POST, PUT, DELETE), `dados` (opcional)

- `enviar_comando`: Envia um comando para a API SkyBridge
  - Parâmetros: `comando`, `parametros` (opcional)

## Como Usar

### Testar com o MCP Inspector

Para testar o servidor com o MCP Inspector, execute:

```bash
mcp dev mcp_server.py
```

### Instalar no Claude Desktop

Para instalar o servidor no Claude Desktop, execute:

```bash
mcp install mcp_server.py
```

## Exemplos de Uso

### Obter Configurações

```
Configs: configs://
```

### Consultar um Endpoint Específico

```
Consultar endpoint: /config com método GET
ou
Consultar prompt de instruções: /file/open?path=docs\planejamento\prompts\instrução_sky.md
```

### Enviar um Comando

```
Enviar comando: atualizar com parâmetros {"force": true}
```

## Solução de Problemas

Se encontrar problemas ao conectar-se à API SkyBridge, verifique:

1. Se o servidor da API está em execução
2. Se as credenciais no arquivo `cli-rest.env` estão corretas
3. Se todas as dependências foram instaladas corretamente

## Desenvolvimento

Para adicionar novos recursos ou ferramentas, edite o arquivo `mcp_server.py` seguindo o padrão existente.