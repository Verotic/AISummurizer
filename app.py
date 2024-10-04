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
        "prompt": f"Resuma o seguinte texto:\n\n{text}",
        "max_tokens": 1000  # Ajuste conforme necessário
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
#pdf_text = extract_text_from_pdf(pdf_file_path)
pdf_text = """"**A Casa do Silêncio**

Era uma noite fria e estrelada quando Maria decidiu visitar a casa 
abandonada que havia sido propriedade de seu avô. A casa era um monstro de 
madeira e tijolo, com janelas que pareciam olhos vazios e portas que se 
abriam como as mãos de um fantasma.

Maria sempre havia sentido uma conexão especial com a casa. Seu avô havia 
morado lá quando era menina, e ela lembrava-se de brincar nos corredores 
frios e de ouvir histórias assustadoras sobre o que acontecia na noite. 
Mas agora, com 25 anos, Maria estava curiosa para descobrir se a história 
do avô era apenas uma lenda.

Quando chegou à casa, Maria sentiu um arrepio em seu pescoço. A porta 
estava trancada, mas ela conseguiu abrir com algum esforço. Em seguida, 
entrou suavemente no interior da casa, chaminho pelas portas estreitas e 
os corredores sinuosos.

À medida que Maria explorava a casa, começou a notar coisas estranhas. A 
iluminação era muito fraca, mas ela conseguia ver uma lâmpada acesa no 
salão principal. Ela se aproximou da luz e viu um velho retrato pendurado 
na parede. O homem do retrato parecia estar olhando diretamente para ela.

De repente, Maria ouviu um barulho atrás dela. Se virou para ver uma porta 
fechada que nunca havia visto antes. Ela se aproximou e a abriu, revelando 
um corredor escuro e sinistro. A voz do seu avô começou a ecoar em sua 
mente: "Não vários."

Maria hesitou por um momento antes de avançar pelo corredor. As paredes 
pareciam estar se movendo e os passos de alguém estavam atrás dela. Ela 
estava começando a perder a sanidade, mas estava determinada a descobrir o 
que acontecia na casa.

Quando chegou ao final do corredor, Maria viu uma porta fechada com uma 
placa que dizia: " Não entre". Mas ela não se importou. Abriu a porta e 
encontrou um quarto pequeno com uma cama simples. Em meio à cama havia 
algo pendurado sobre o colo do avô, e era uma foto de Maria.

De repente, as portas da casa começaram a se fechar sozinhas, e Maria 
ouviu uma voz que parecia ser de seu avô. "Você não deve ter entrado 
aqui", disse. "Agora é tarde demais".

Maria tentou sair do quarto, mas estava preso. As portas estavam trancadas 
e a janela estava fechada. Ela começou a gritar por ajuda, mas ninguém 
veio. O silêncio era opressivo e Maria sabia que ela nunca mais seria 
vista.

A casa do silêncio passou a ser uma lenda, e as pessoas diziam que os 
fantasmas do avô e de Maria ainda estavam lá, esperando por alguém que 
quisesse ouvir suas histórias assustadoras."""
# Resumir o texto extraído
resumo = summarize_text_with_llama(pdf_text)

# Exibir o resumo
print("Resumo do PDF:")
print(resumo)
