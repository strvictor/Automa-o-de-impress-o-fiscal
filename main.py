import time, datetime
import pdfplumber
import re
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from escpos.printer import Network


# Configurações
PASTA_MONITORADA = "C:/RecibosAutomaticos"
if not os.path.exists(PASTA_MONITORADA):
    os.makedirs(PASTA_MONITORADA)
IMPRESSORA_IP = "192.168.0.174" #ip local da impressora
IMPRESSORA_PORTA = 9100 # padrão
LARGURA_IMPRESSORA = 48 # largura padrão da epson tm-t20

# ----------------------------------------------
# Funções de Processamento de PDF
# ----------------------------------------------
def extrair_texto_pdf(caminho_pdf):
    time.sleep(2)
    """Extrai texto de um PDF (text-based)"""
    try:
        caminho_corrigido = os.path.normpath(caminho_pdf)
        with pdfplumber.open(caminho_corrigido) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() + "\n"
            print(texto)
            return texto
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return None

def processar_dados(texto):
    """Extrai itens e total do texto"""
    try:
        padrao = r"""
RECIBO\sDE\sPAGAMENTO\sNº\s*:\s*(\d+).*?  # Número do recibo
(Declaro\s+por\s+meio\s+deste\s+que\s+recebi\s+de\s+.*?parcela\s+\d+/\d+)  # Texto da declaração
"""
        matches = re.search(padrao, texto, re.DOTALL | re.IGNORECASE | re.VERBOSE)
        if matches:
            numero_recibo = matches.group(1)
            texto_declaracao = matches.group(2).replace("\n", " ")  # Remove quebras de linha
            print(f"Número do recibo: {numero_recibo}")
            print(f"Texto da declaração: {texto_declaracao}")
            return {
                "numero_recibo": numero_recibo if numero_recibo else '',
                "descricao": texto_declaracao if texto_declaracao else '',
            }
        else:
            return {
                "numero_recibo": '',
                "descricao": '',
            }
            
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return {
            "numero_recibo": '',
            "descricao": '',
        }
        

def formatar_impressao(dados):
    """Formata os dados para o layout da impressora"""
    data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        texto = ""
        # Cabeçalho centralizado
        texto += "\x1B\x61\x01"  # Comando ESC/POS para alinhamento centralizado
        texto += " ASSOCIACAO RECREATIVA CABANA CLUBE \n"
        texto += " AV. DOM ROMUALDO COELHO, 401 \n"
        texto += " VILA DOS CABANOS - BARCARENA PA \n"
        texto += " CNPJ - 63.886.204/0001-91 \n"
        texto += f" COMPROVANTE FISCAL N {dados['numero_recibo']} \n"
        texto += f" {data_hora} \n\n"
        texto += "\x1B\x61\x00"  # Volta alinhamento para esquerda
        
        # descrição
        texto += "=" * LARGURA_IMPRESSORA + "\n\n"
        texto += f" {dados['descricao']} \n\n"
        texto += "=" * LARGURA_IMPRESSORA + "\n\n\n"
        
        texto += "\x1B\x61\x01"  # Comando ESC/POS para alinhamento centralizado
        texto += " _______________________________________ \n"
        texto += " Assinatura \n\n"
        texto += "\x1B\x61\x00"  # Volta alinhamento para esquerda
        
        
        # Rodapé
        texto += "\nObrigado pela preferencia!"
        return texto
    except Exception as e:
        print(f"Erro ao formatar impressão: {e}")
        return None

# ----------------------------------------------
# Classe para Monitorar a Pasta
# ----------------------------------------------
class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            caminho_pdf = os.path.normpath(event.src_path)
            print(f"\nNovo PDF detectado: {caminho_pdf}")
            time.sleep(2)
            texto = extrair_texto_pdf(caminho_pdf)
            if texto:
                dados = processar_dados(texto)
                if dados:
                    texto_impressao = formatar_impressao(dados)
                    if texto_impressao:
                        imprimir(texto_impressao)

# ----------------------------------------------
# Função de Impressão (Modificada para controle de formatação)
# ----------------------------------------------
def imprimir(texto):
    try:
        p = Network(IMPRESSORA_IP, IMPRESSORA_PORTA, timeout=5)
        p.set(
            align="left",
            width=1,
            height=1,
            font="a"
        )
        # Envia o texto já formatado com comandos ESC/POS
        p._raw(texto.encode('utf-8'))  # Envia comandos diretamente
        p.cut()
        print("Impressão concluída com sucesso!")
    except Exception as e:
        print(f"Erro na impressão: {e}")
    finally:
        p.close()

# ----------------------------------------------
# Iniciar Monitoramento
# ----------------------------------------------

event_handler = PDFHandler()
observer = Observer()
observer.schedule(event_handler, PASTA_MONITORADA, recursive=False)

print(f"Monitorando pasta: {PASTA_MONITORADA}")
print("Pressione Ctrl+C para parar...")

observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
