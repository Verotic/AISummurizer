import os
import PyPDF2
import requests
import json


print("Starting main function")


# Função para resumir texto usando o modelo Llama via API Ollama
def summarize_text_with_llama(text):
    print("Starting summarize_text_with_llama function")
    url = "http://localhost:11434/api/generate"  # Verifique o endereço correto da API

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        
        "model": "llama3.2",
        "prompt": f"Could you please provide a concise and comprehensive summary of the given text? The summary should capture the main points and key details of the text while conveying the author's intended meaning accurately. Please ensure that the summary is well-organized and easy to read, with clear headings and subheadings to guide the reader through each section. The length of the summary should be appropriate to capture the main points and key details of the text, without including unnecessary information or becoming overly long.\n\n{text}",
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

            print("Finishing summarize_text_with_llama function")
            return resumo_completo.strip()
        
        except Exception as e:
            raise Exception(f"Erro ao processar a resposta da API: {e}")
    else:
        raise Exception(f"Erro ao se conectar à API Llama: {response.status_code} {response.text}")



# Extrair texto do PDF
def extract_text_from_pdf(pdf_path):

    print("Starting extract_text_from_pdf function")

    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            print("Finishing extract_text_from_pdf function")
            return text
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo PDF: {e}")
# Resumir o texto extraído

def list_books(directory):
    print("Starting list_books function")
    try:
        return [f for f in os.listdir(directory) if f.endswith('.pdf')]
    except FileNotFoundError:
        print(f"Pasta '{directory}' não encontrada.")
        return []
def select_book(books):

    print("Starting select_book function")
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
                print("Finishing select_book function")
                return books[choice - 1]
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Insira um número.")
            
def save_summary_to_file(summary, book_name):
    if not summary or not book_name:
        raise ValueError("Summary and book name cannot be empty")

    # Nome do arquivo de resumo
    summary_file_name = f"Resumo_{os.path.splitext(book_name)[0]}.txt"
    print(f"Summary file name: {summary_file_name}")

    # Caminho completo para salvar o arquivo
    summary_file_path = os.path.join(os.path.dirname(__file__), 'resumos', summary_file_name)
    print(f"Summary file path: {summary_file_path}")

    try:
        # Criar pasta 'resumos' se não existir
        os.makedirs(os.path.dirname(summary_file_path), exist_ok=True)
        print(f"Directory exists: {os.path.exists(os.path.dirname(summary_file_path))}")

        # Verificar permissões de escrita
        if os.access(os.path.dirname(summary_file_path), os.W_OK):
            print("Directory has write permissions")
        else:
            print("Directory does not have write permissions")

        # Escrever o resumo no arquivo de texto
        with open(summary_file_path, 'w', encoding='utf-8') as file:
            file.write(summary)
            print("File written successfully")
        
        print(f"\nResumo salvo em: {summary_file_path}")
    except OSError as e:
        print(f"Erro ao salvar o resumo: {e}")
    except Exception as e:
        print(f"Erro inesperado ao salvar o resumo: {e}")

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
