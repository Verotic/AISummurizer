# Importa as bibliotecas necessarias
import nltk
import unicodedata

# Baixa o modelo de tokenizacao necessario para a biblioteca nltk
nltk.download('punkt')

# Importa a funcao de tokenizacao por sentenca
from nltk.tokenize import sent_tokenize

# Define uma funcao para remover caracteres acentuados de um texto
def remove_accented_chars(text):
    """
    Recebe um texto e remove todos os caracteres acentuados, 
    convertendo-os para o caracter equivalente sem acento.
    """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

# Define um texto de exemplo
texto = """Texto de exemplo"""

# Tokeniza o texto em sentencas
sentencas = sent_tokenize(texto, language='portuguese')

# Imprime as sentencas tokenizadas
for i, sentenca in enumerate(sentencas, start=1):
    print(f"Sentenca {i}: {sentenca}")

# Normaliza as sentencas removendo duplo espaco e convertendo para min sculo
sentencas_normalizadas = [remove_accented_chars(sentenca.replace("  ", " ").lower()) for sentenca in sentencas]

# Imprime as sentencas normalizadas
for i, sentenca in enumerate(sentencas_normalizadas, start=1):
    print(f"Sentenca normalizada {i}: {sentenca}")

