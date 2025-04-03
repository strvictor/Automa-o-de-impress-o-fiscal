# Monitoramento e Impressão Automática de Recibos

Este projeto monitora uma pasta específica em busca de arquivos PDF, extrai informações relevantes e imprime automaticamente em uma impressora de rede.

## Funcionalidades

- Monitora automaticamente a pasta `C:/RecibosAutomaticos`.
- Extrai informações do PDF, como número do recibo e descrição.
- Formata os dados de acordo com o layout da impressora.
- Envia o recibo formatado para uma impressora de rede compatível com ESC/POS.

## Requisitos

- Python 3.x
- Biblioteca `pdfplumber` para extração de texto de PDFs.
- Biblioteca `watchdog` para monitoramento de arquivos.
- Biblioteca `python-escpos` para comunicação com a impressora.

## Configuração

Edite as variáveis no código para adaptar ao seu ambiente:

- ``: Endereço IP da impressora de rede.
- ``: Porta padrão da impressora (geralmente `9100`).
- ``: Largura do texto da impressora.

## Uso

Execute o script para iniciar o monitoramento:

```sh
python main.py
```

O programa irá aguardar novos arquivos PDF na pasta e os imprimirá automaticamente.

## Personalização

Se necessário, ajuste a função `processar_dados` para extrair diferentes informações dos PDFs.

## Licença

Este projeto é de uso interno e pode ser adaptado conforme necessário.

