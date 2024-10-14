from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import docx
from infinitive import extract_text_from_docx, tokenize_sentences, extract_verbs, convert_to_infinitive, replace_verbs_with_infinitive, remove_accented_chars
import requests
import json

# Define the path to the uploads folder relative to the Server folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store the modified text for chat processing
modified_text_storage = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to summarize text using the Llama model via API Ollama with late chunking
def summarize_text_with_llama(text, question):
    url = "http://localhost:11434/api/generate"  # Verifique o endereço correto da API

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3.2",
        "prompt": f"Resposta:\n\n{text}Pergunta:\n\n{question}",
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


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            print("No file part in the request")
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            print("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"File saved to {file_path}")
            return redirect(url_for('process_file', filename=filename))
        else:
            print("File not allowed")
    return render_template('index.html')

@app.route('/process/<filename>')
def process_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return redirect(url_for('upload_file'))
    
    text = extract_text_from_docx(file_path)
    
    # Normalize the text by removing accents and extra spaces
    text = remove_accented_chars(text)
    text = ' '.join(text.split()).lower()
    
    sentences = tokenize_sentences(text)
    verbs = extract_verbs(sentences)
    infinitive_verbs = convert_to_infinitive(verbs)
    modified_text = replace_verbs_with_infinitive(text)

    # Save the modified text back to a new DOCX file
    modified_docx_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace('.docx', '_modified.docx'))
    doc = docx.Document()
    for paragraph in modified_text.split('\n'):
        doc.add_paragraph(paragraph)
    doc.save(modified_docx_path)
    print(f"Modified file saved to {modified_docx_path}")

    # Store the modified text for chat processing
    modified_text_storage[filename] = modified_text

    return render_template('result.html', modified_file=filename.replace('.docx', '_modified.docx'), original_file=filename)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    filename = data.get('filename')
    question = data.get('question')

    if filename not in modified_text_storage:
        return jsonify({'error': 'File not found'}), 404

    modified_text = modified_text_storage[filename]

    # Summarize the text using the Llama model
    try:
        answer = summarize_text_with_llama(modified_text, question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)