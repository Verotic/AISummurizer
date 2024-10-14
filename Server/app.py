from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import docx
from infinitive import extract_text_from_docx, tokenize_sentences, extract_verbs, convert_to_infinitive, replace_verbs_with_infinitive, remove_accented_chars
#teste
# Define the path to the uploads folder relative to the Server folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    return render_template('result.html', modified_file=filename.replace('.docx', '_modified.docx'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)