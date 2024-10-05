import os
import PyPDF2
import requests
import json



# Função para resumir texto usando o modelo Llama via API Ollama
def summarize_text_with_llama(text):
    url = "http://localhost:11434/api/generate"  # Verifique o endereço correto da API

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3.2",
        "prompt": f"Resuma o seguinte livro detalhadamente:\n\n{text}",
        "max_tokens": 128256  # Ajuste conforme necessário
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        try:
            # Pegue o conteúdo bruto da resposta como texto
            raw_text = response.text

            # Divide o texto bruto em possíveis fragmentos de JSON
            json_fragments = raw_text.splitlines()

            # Variável para armazenar a resposta completa
            resumo_completo = ""

            for fragment in json_fragments:
                # Tenta carregar cada fragmento como JSON
                try:
                    json_data = json.loads(fragment)
                    if 'response' in json_data:
                        resumo_completo += json_data['response']  # Concatena o fragmento
                    if json_data.get('done', False):  # Verifica se é o último fragmento
                        break
                except json.JSONDecodeError:
                    continue  # Se o fragmento não for JSON, passa para o próximo

            if not resumo_completo: 
                resumo_completo = "Sem resumo disponível."

            return resumo_completo.strip()
        
        except Exception as e:
            raise Exception(f"Erro ao processar a resposta da API: {e}")

    else:
        raise Exception(f"Erro ao se conectar à API Llama: {response.status_code} {response.text}")


# Extrair texto do PDF
def extract_text_from_pdf(pdf_path):

    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo PDF: {e}")
# Resumir o texto extraído

def list_books(directory):
    try:
        return [f for f in os.listdir(directory) if f.endswith('.pdf')]
    except FileNotFoundError:
        print(f"Pasta '{directory}' não encontrada.")
        return []
def select_book(books):
    if not books:
        print("Nenhum livro encontrado.")
        return None
    
    print("Livros disponíveis para resumir:")
    for i, book in enumerate(books, 1):
        print(f"{i}. {book}")

    while True:
        try:
            choice = int(input("\nSelecione o número do livro que deseja resumir: "))
            if 1 <= choice <= len(books):
                return books[choice - 1]
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Insira um número.")

books_dir = os.path.join(os.path.dirname(__file__), 'books')

books = list_books(books_dir)
selected_book = select_book(books)


if selected_book:
    # Caminho completo do livro selecionado
    pdf_path = os.path.join(books_dir, selected_book)

    # Extrair o texto do PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Resumir o texto extraído
    if pdf_text.strip():
        resumo = summarize_text_with_llama(pdf_text)
        print("\nResumo do PDF:")
        print(resumo)
    else:
        print("Nenhum texto encontrado no PDF.")
