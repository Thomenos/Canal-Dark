import asyncio

import edge_tts

import os

import requests

import hashlib

import glob

import google.generativeai as genai

from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip

# Imports para YouTube Upload

from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build

from googleapiclient.http import MediaFileUpload

from google.auth.transport.requests import Request

import pickle

 

# --- ⚙️ CONFIGURAÇÕES ---

CHAVE_GEMINI = "AIzaSyAnXVzjOqmpminxO22SP4bJkJc6X0EYyIE" # Se for usar geração de texto automática

ARQUIVO_TEXTO = "historia.txt"

ARQUIVO_HASH = "historia.txt.hash"  # Salva hash do último texto processado

PASTA_VIDEOS = "videos_gerados"  # Pasta onde os vídeos serão salvos

NOME_AUDIO = "narracao_atual.mp3"  # Áudio temporário (será regenerado se texto mudar)

# NOME_VIDEO agora é gerado automaticamente (ex: video_001.mp4, video_002.mp4)



# Renderização

PRESET_RENDERIZACAO = "faster"  # Opções: "ultrafast" (mais rápido), "faster" (rápido), "medium" (qualidade)

THREADS_RENDERIZACAO = 10  # Threads para usar (máx: 12 no Ryzen 5 8600G) - mais threads = mais CPU



# Pastas

PASTA_VIDEOS_INTRO = "videos_hailuo" # Intro impactante

PASTA_BACKGROUND = "background_loop" # Pasta para o fundo do vídeo longo



# Voz (Brian para narrar 1 hora é cansativo? Talvez testar outras, mas o Brian é bom)

VOZ = "en-US-BrianMultilingualNeural"



# GIF de Call-to-Action (CTA)

GIF_INSCRICAO = "inscricao.gif"  # Caminho para o GIF de inscrição

ATIVAR_GIF_CTA = True  # True para ativar overlay de GIF quando o texto pedir para se inscrever



# YouTube Upload

FAZER_UPLOAD_YOUTUBE = True  # True para fazer upload automático, False para não

ARQUIVO_CREDENCIAIS_YOUTUBE = "client_secret.json"  # Arquivo de credenciais OAuth2

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

 

# --- FUNÇÕES ---

def baixar_background_ia(tema):

    print(f"   🎨 Gerando Background Atmosférico para o tema '{tema}'...")

    if not os.path.exists(PASTA_BACKGROUND):

        os.makedirs(PASTA_BACKGROUND)

 

    caminho = os.path.join(PASTA_BACKGROUND, "bg_principal.jpg")

 

    # Prompt focado em "Ambiente" e não em "Ação"

    prompt = f"dark horror atmosphere background, {tema}, seamless texture, 4k, cinematic lighting, mysterious, no text, subtle"

    url_prompt = prompt.replace(" ", "%20")

 

    try:

        # Pede imagem Widescreen (1920x1080) para vídeo longo de YouTube

        url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1920&height=1080&nologo=true"

        resposta = requests.get(url, timeout=60)

        if resposta.status_code == 200:

            with open(caminho, 'wb') as f:

                f.write(resposta.content)

            return caminho

    except Exception as e:

        print(f"❌ Erro ao baixar background: {e}")

    return None



def efeito_pulso(clip, intensidade=0.05, velocidade=8):
    """
    Aplica efeito de pulso/respiração na imagem.

    intensidade: quanto a imagem vai "respirar" (0.05 = 5% de zoom)
    velocidade: duração de cada ciclo de respiração em segundos
    """
    import math

    def fazer_pulso(get_frame, t):
        # Cria uma onda senoidal para o efeito de respiração
        # math.sin varia de -1 a 1, ajustamos para 1.0 ± intensidade
        escala = 1.0 + intensidade * math.sin(2 * math.pi * t / velocidade)

        # Pega o frame atual
        frame = get_frame(t)

        # Calcula o novo tamanho
        h, w = frame.shape[:2]
        novo_h = int(h * escala)
        novo_w = int(w * escala)

        # Importa cv2 para resize (mais rápido que PIL para vídeos)
        import cv2
        frame_resized = cv2.resize(frame, (novo_w, novo_h))

        # Centraliza o crop para manter 1920x1080
        if novo_h > h or novo_w > w:
            # Se aumentou, corta o excesso
            start_y = (novo_h - h) // 2
            start_x = (novo_w - w) // 2
            return frame_resized[start_y:start_y+h, start_x:start_x+w]
        else:
            # Se diminuiu, adiciona padding preto
            top = (h - novo_h) // 2
            left = (w - novo_w) // 2
            import numpy as np
            resultado = np.zeros_like(frame)
            resultado[top:top+novo_h, left:left+novo_w] = frame_resized
            return resultado

    return clip.fl(fazer_pulso)



def calcular_hash_arquivo(caminho_arquivo):
    """
    Calcula o hash MD5 de um arquivo de texto.
    Usado para detectar se o conteúdo mudou.
    """
    if not os.path.exists(caminho_arquivo):
        return None

    with open(caminho_arquivo, 'rb') as f:
        conteudo = f.read()
        return hashlib.md5(conteudo).hexdigest()



def historia_mudou():
    """
    Verifica se o arquivo historia.txt foi modificado desde a última vez.
    Retorna True se mudou, False se está igual.
    """
    hash_atual = calcular_hash_arquivo(ARQUIVO_TEXTO)

    if hash_atual is None:
        return False  # Arquivo não existe

    # Verifica se existe hash salvo
    if not os.path.exists(ARQUIVO_HASH):
        return True  # Primeira vez, precisa gerar

    # Lê o hash salvo
    with open(ARQUIVO_HASH, 'r') as f:
        hash_salvo = f.read().strip()

    return hash_atual != hash_salvo



def salvar_hash_atual():
    """
    Salva o hash do arquivo historia.txt atual.
    Chamado depois de gerar o áudio com sucesso.
    """
    hash_atual = calcular_hash_arquivo(ARQUIVO_TEXTO)

    if hash_atual:
        with open(ARQUIVO_HASH, 'w') as f:
            f.write(hash_atual)



def gerar_proximo_nome_video():
    """
    Gera o próximo nome de vídeo sequencial (video_001.mp4, video_002.mp4, etc).
    Cria a pasta videos_gerados se não existir.
    """
    # Cria pasta se não existir
    if not os.path.exists(PASTA_VIDEOS):
        os.makedirs(PASTA_VIDEOS)
        print(f"   ✅ Pasta '{PASTA_VIDEOS}' criada!")

    # Busca todos os vídeos existentes
    videos_existentes = glob.glob(os.path.join(PASTA_VIDEOS, "video_*.mp4"))

    if not videos_existentes:
        # Primeiro vídeo
        numero = 1
    else:
        # Pega o maior número existente
        numeros = []
        for video in videos_existentes:
            nome = os.path.basename(video)
            # Extrai número do nome (video_001.mp4 -> 001)
            try:
                num_str = nome.replace("video_", "").replace(".mp4", "")
                numeros.append(int(num_str))
            except:
                pass

        numero = max(numeros) + 1 if numeros else 1

    # Formato: video_001.mp4, video_002.mp4, etc
    nome_video = os.path.join(PASTA_VIDEOS, f"video_{numero:03d}.mp4")

    return nome_video



def detectar_momentos_cta(texto):
    """
    Detecta momentos no texto onde há chamadas para ação (CTA).
    Retorna lista de frases que contêm CTAs.
    """
    cta_palavras = [
        "inscreva",
        "inscreve",
        "inscrição",
        "se inscrever",
        "deixe seu like",
        "curtir",
        "compartilhe",
        "compartilhar",
        "ative o sino",
        "notificações"
    ]

    # Divide o texto em frases (por ponto final, exclamação ou interrogação)
    import re
    frases = re.split(r'[.!?]+', texto.lower())

    momentos_cta = []
    for frase in frases:
        for palavra_cta in cta_palavras:
            if palavra_cta in frase:
                momentos_cta.append(frase.strip())
                break  # Evita duplicatas da mesma frase

    return momentos_cta



async def gerar_audio_com_timestamps(texto, arquivo_saida):
    """
    Gera áudio e captura os timestamps das palavras.
    Retorna uma lista de timestamps onde aparecem CTAs.
    """
    print("   -> Gerando áudio com timestamps...")

    comunicacao = edge_tts.Communicate(texto, VOZ)

    # Detecta palavras-chave de CTA
    cta_palavras = [
        "inscreva", "inscreve", "inscrição", "inscrever",
        "like", "curtir", "compartilhe", "compartilhar",
        "sino", "notificações"
    ]

    timestamps_cta = []

    # Salva o áudio e captura os timestamps em tempo real
    with open(arquivo_saida, "wb") as arquivo:
        async for chunk in comunicacao.stream():
            if chunk["type"] == "audio":
                arquivo.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Processa cada palavra em tempo real
                palavra = chunk["text"].lower()
                for cta in cta_palavras:
                    if cta in palavra:
                        # Converte de nanosegundos para segundos
                        tempo_seg = chunk["offset"] / 10_000_000.0
                        timestamps_cta.append(tempo_seg)
                        print(f"   -> CTA detectado em {tempo_seg:.1f}s: '{chunk['text']}'")
                        break

    if timestamps_cta:
        print(f"   ✅ Total de {len(timestamps_cta)} CTA(s) detectado(s)!")
    else:
        print(f"   ⚠️ Nenhum CTA detectado no texto.")

    return timestamps_cta



def adicionar_gif_overlay(video_clip, gif_path, timestamps, duracao_gif=3.0, posicao="canto"):
    """
    Adiciona GIF como overlay no vídeo nos timestamps especificados.

    posicao: "canto" (superior direito), "centro", "baixo"
    duracao_gif: quanto tempo o GIF fica na tela (em segundos)
    """
    if not os.path.exists(gif_path):
        print(f"⚠️ GIF não encontrado: {gif_path}")
        return video_clip

    if not timestamps:
        print("   -> Nenhum CTA detectado, pulando overlay de GIF")
        return video_clip

    print(f"   -> Adicionando GIF em {len(timestamps)} momento(s)...")

    # Carrega o GIF
    try:
        gif_clip = VideoFileClip(gif_path, has_mask=True)

        # Redimensiona o GIF (não muito grande)
        gif_clip = gif_clip.resize(width=300)

        # Define a posição
        if posicao == "canto":
            # Canto superior direito
            gif_clip = gif_clip.set_position((1920 - 320, 20))
        elif posicao == "centro":
            # Centro da tela
            gif_clip = gif_clip.set_position("center")
        elif posicao == "baixo":
            # Centro inferior
            gif_clip = gif_clip.set_position(("center", 1080 - gif_clip.h - 50))

        # Cria um clip de GIF para cada timestamp
        gif_overlays = []
        for timestamp in timestamps:
            # Define quando o GIF aparece e desaparece
            gif_temp = gif_clip.copy()
            gif_temp = gif_temp.set_start(timestamp).set_duration(duracao_gif)

            # Adiciona fade in/out suave
            gif_temp = gif_temp.crossfadein(0.3).crossfadeout(0.3)

            gif_overlays.append(gif_temp)

        # Combina o vídeo original com todos os GIFs
        video_com_gifs = CompositeVideoClip([video_clip] + gif_overlays)

        print(f"   ✅ {len(timestamps)} GIF(s) adicionado(s) com sucesso!")
        return video_com_gifs

    except Exception as e:
        print(f"⚠️ Erro ao adicionar GIF: {e}")
        return video_clip



def gerar_titulo_descricao_gemini(texto_historia):
    """
    Gera título e descrição para o vídeo usando Gemini AI.
    """
    try:
        if CHAVE_GEMINI == "COLE_SUA_CHAVE_AQUI":
            print("⚠️  Chave Gemini não configurada. Usando título padrão.")
            return {
                "titulo": "História de Terror - Canal Dark",
                "descricao": "Uma narrativa sombria e atmosférica de terror.\n\n#terror #dark #história"
            }

        genai.configure(api_key=CHAVE_GEMINI)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Pega os primeiros 500 caracteres da história
        resumo_historia = texto_historia[:500]

        prompt = f"""Você é um especialista em marketing para YouTube no nicho de terror/dark.

Com base nesta história de terror:
{resumo_historia}...

Gere:
1. Um TÍTULO chamativo e otimizado para SEO (máximo 80 caracteres)
2. Uma DESCRIÇÃO completa e envolvente (200-300 palavras) que:
   - Desperte curiosidade sem spoilers
   - Use palavras-chave de terror/mistério
   - Inclua hashtags relevantes (#terror #dark #horror #creepypasta)
   - Mencione que é narrado por IA

Formato da resposta:
TÍTULO: [seu título aqui]
DESCRIÇÃO: [sua descrição aqui]
"""

        response = model.generate_content(prompt)
        resultado = response.text

        # Extrai título e descrição
        linhas = resultado.split('\n')
        titulo = ""
        descricao = ""

        capturando_descricao = False
        for linha in linhas:
            if linha.startswith("TÍTULO:"):
                titulo = linha.replace("TÍTULO:", "").strip()
            elif linha.startswith("DESCRIÇÃO:"):
                descricao = linha.replace("DESCRIÇÃO:", "").strip()
                capturando_descricao = True
            elif capturando_descricao:
                descricao += "\n" + linha

        # Limita o título a 100 caracteres (limite do YouTube)
        if len(titulo) > 100:
            titulo = titulo[:97] + "..."

        print(f"✅ Título gerado: {titulo}")
        print(f"✅ Descrição gerada: {descricao[:100]}...")

        return {
            "titulo": titulo if titulo else "História de Terror - Canal Dark",
            "descricao": descricao if descricao else "Uma narrativa sombria e atmosférica."
        }

    except Exception as e:
        print(f"❌ Erro ao gerar metadados com Gemini: {e}")
        return {
            "titulo": "História de Terror - Canal Dark",
            "descricao": "Uma narrativa sombria e atmosférica de terror.\n\n#terror #dark #história"
        }



def autenticar_youtube():
    """
    Autentica no YouTube usando OAuth2.
    """
    creds = None

    # Verifica se já existe token salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Se não há credenciais válidas, faz login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(ARQUIVO_CREDENCIAIS_YOUTUBE):
                print(f"❌ Arquivo {ARQUIVO_CREDENCIAIS_YOUTUBE} não encontrado!")
                print("   Siga as instruções em YOUTUBE_SETUP.txt para configurar.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                ARQUIVO_CREDENCIAIS_YOUTUBE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva as credenciais para próxima vez
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)



def fazer_upload_youtube(arquivo_video, titulo, descricao):
    """
    Faz upload do vídeo para o YouTube como privado.
    """
    try:
        print("\n📤 Iniciando upload para YouTube...")

        youtube = autenticar_youtube()
        if not youtube:
            return None

        body = {
            'snippet': {
                'title': titulo,
                'description': descricao,
                'tags': ['terror', 'dark', 'horror', 'creepypasta', 'história', 'mistério'],
                'categoryId': '24'  # Categoria: Entretenimento
            },
            'status': {
                'privacyStatus': 'private',  # PRIVADO por padrão
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(arquivo_video, chunksize=-1, resumable=True)

        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        print("   -> Fazendo upload... (Isso pode demorar)")

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   -> Upload: {progress}% concluído")

        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"\n✅ VÍDEO ENVIADO COM SUCESSO!")
        print(f"🔗 URL: {video_url}")
        print(f"🔒 Status: PRIVADO (você pode tornar público depois)")
        print(f"📝 Título: {titulo}")

        return video_url

    except Exception as e:
        print(f"\n❌ Erro ao fazer upload: {e}")
        return None



async def criar_video_longo():

    print("--- INICIANDO MODO VÍDEO LONGO (40-60min) ---")

 

    # 1. ÁUDIO (O MAIS IMPORTANTE)

    print(f"\n📖 1. Verificando áudio...")



    # NOVA LÓGICA: Detecta automaticamente se o texto mudou

    timestamps_cta = []  # Lista de timestamps onde aparecem CTAs

    texto_mudou = historia_mudou()



    if not os.path.exists(ARQUIVO_TEXTO):

        print("❌ Crie o arquivo historia.txt com sua história longa!")

        return



    # Verifica se precisa regenerar o áudio

    if os.path.exists(NOME_AUDIO) and not texto_mudou:

        print("   -> Áudio já existe e o texto não mudou. Reutilizando áudio anterior.")

        print("   💡 Dica: Edite historia.txt para gerar um novo vídeo automaticamente!")

    else:

        if texto_mudou:

            print("   🆕 NOVA HISTÓRIA DETECTADA! Gerando novo áudio...")

        else:

            print("   -> Gerando narração longa (Isso pode demorar uns minutos)...")



        with open(ARQUIVO_TEXTO, "r", encoding="utf-8") as f:

            texto = f.read()



        # Gera áudio COM timestamps de CTAs

        if ATIVAR_GIF_CTA:

            timestamps_cta = await gerar_audio_com_timestamps(texto, NOME_AUDIO)

        else:

            comunicacao = edge_tts.Communicate(texto, VOZ)

            await comunicacao.save(NOME_AUDIO)



        # Salva o hash do texto processado

        salvar_hash_atual()

        print("   ✅ Hash da história salvo para detecção automática de mudanças!")



    # Carrega áudio para saber a duração

    audio_clip = AudioFileClip(NOME_AUDIO)

    tempo_total = audio_clip.duration

    print(f"✅ Duração Total do Áudio: {tempo_total/60:.2f} minutos ({tempo_total:.0f}s).")

 

    lista_clips_intro = []

    tempo_intro = 0

 

    # 2. INTRODUÇÃO (VÍDEOS HAILUO)

    print("\n🎥 2. Preparando Introdução (Hailuo)...")

    if os.path.exists(PASTA_VIDEOS_INTRO):

        videos = sorted([f for f in os.listdir(PASTA_VIDEOS_INTRO) if f.endswith(".mp4")])

        for v in videos:

            path = os.path.join(PASTA_VIDEOS_INTRO, v)

            try:

                # Resize para 1920x1080 (Padrão YouTube)

                clip = VideoFileClip(path).without_audio().resize(height=1080)

                # Garante que é 16:9 cortando as bordas se necessário

                clip = clip.crop(x1=clip.w/2 - 960, y1=0, width=1920, height=1080)

                lista_clips_intro.append(clip)

                tempo_intro += clip.duration

                print(f"   -> Intro adicionada: {v} ({clip.duration:.1f}s)")

            except Exception as e:

                print(f"   ⚠️ Erro no vídeo {v}: {e}")

 

    # 3. CORPO DO VÍDEO (LOOP INFINITO)

    tempo_restante = tempo_total - tempo_intro

    clip_background = None

 

    if tempo_restante > 0:

        print(f"\n🎨 3. Preparando Background para os {tempo_restante/60:.2f} minutos restantes...")

 

        # Tenta achar uma imagem na pasta background, senão gera uma

        caminho_bg = os.path.join(PASTA_BACKGROUND, "bg_principal.jpg")

 

        if not os.path.exists(caminho_bg):

            tema = input("👻 Não achei imagem de fundo. Sobre o que é a história? (ex: floresta, casa): ")

            caminho_bg = baixar_background_ia(tema)

 

        if caminho_bg and os.path.exists(caminho_bg):

            # Cria um clip de imagem

            img_clip = ImageClip(caminho_bg)

 

            # TRUQUE: Em vez de criar um vídeo de 1 hora (que explode a memória RAM),

            # nós dizemos para o MoviePy: "Essa imagem dura X segundos".

            # Para dar uma vida, vamos aplicar um efeito de "respiração" (zoom muito lento)

            # Mas zoom em vídeo de 1 hora demora muito. Vamos fazer estático com fade in/out

            # ou simplesmente estático para garantir que renderize.

 

            # Configura o clip base
            clip_background = img_clip.set_duration(tempo_restante).resize(height=1080).set_fps(24)

            # Centraliza crop 16:9
            clip_background = clip_background.crop(x1=clip_background.w/2 - 960, y1=0, width=1920, height=1080)

            # 🌟 APLICA EFEITO DE PULSO/RESPIRAÇÃO
            print(f"   -> Aplicando efeito de pulso atmosférico...")
            clip_background = efeito_pulso(clip_background, intensidade=0.03, velocidade=10)

            print(f"   -> Background configurado: {tempo_restante:.1f}s (com efeito de pulso)")

 

        else:

            print("❌ Erro crítico: Sem imagem de fundo.")

            audio_clip.close()

            return

 

    # 4. MONTAGEM FINAL

    print("\n💾 4. Montando a linha do tempo...")

    clips_finais = lista_clips_intro.copy()

    if clip_background:

        clips_finais.append(clip_background)

 

    if not clips_finais:

        print("❌ Nenhum clip de vídeo foi criado!")

        audio_clip.close()

        return

 

    # Concatena todos os vídeos

    print("   -> Concatenando clips de vídeo...")

    video_final = concatenate_videoclips(clips_finais, method="compose")

 

    # CORREÇÃO CRÍTICA: Ajusta a duração do vídeo para corresponder exatamente ao áudio

    print(f"   -> Duração do vídeo antes do ajuste: {video_final.duration:.1f}s")

    print(f"   -> Duração do áudio: {audio_clip.duration:.1f}s")

 

    if video_final.duration > audio_clip.duration:

        # Se vídeo for maior que áudio, corta o vídeo

        print("   -> Cortando vídeo para bater com o áudio...")

        video_final = video_final.subclip(0, audio_clip.duration)

    elif video_final.duration < audio_clip.duration:

        # Se vídeo for menor que áudio, estende o último frame

        print("   -> Estendendo vídeo para bater com o áudio...")

        diferenca = audio_clip.duration - video_final.duration

        ultimo_frame = video_final.to_ImageClip(t=video_final.duration - 0.1)

        extensao = ultimo_frame.set_duration(diferenca)

        video_final = concatenate_videoclips([video_final, extensao])

 

    # APLICA O ÁUDIO NO VÍDEO

    print("   -> Aplicando áudio ao vídeo...")

    video_final = video_final.set_audio(audio_clip)

 

    # Verifica se o áudio foi aplicado

    if video_final.audio is None:

        print("❌ ERRO: O áudio não foi aplicado corretamente!")

        return

    else:

        print("   ✅ Áudio aplicado com sucesso!")



    # 4.5 ADICIONA GIF DE INSCRIÇÃO (SE HOUVER CTAs)

    if ATIVAR_GIF_CTA and timestamps_cta:
        print(f"\n🎨 4.5. Adicionando GIF de inscrição em {len(timestamps_cta)} momento(s)...")
        video_final = adicionar_gif_overlay(
            video_final,
            GIF_INSCRICAO,
            timestamps_cta,
            duracao_gif=3.0,  # GIF fica 3 segundos na tela
            posicao="canto"   # Pode mudar para "centro" ou "baixo"
        )
    elif ATIVAR_GIF_CTA and not timestamps_cta:
        print("\n⚠️ Nenhum CTA detectado no áudio. GIF não será adicionado.")



    print(f"   -> Duração final do vídeo: {video_final.duration:.1f}s")



    # 5. RENDERIZAÇÃO

    print("\n🚀 RENDERIZANDO (Isso vai demorar, vá tomar um café)...")



    # GERA NOME AUTOMÁTICO PARA O VÍDEO (video_001.mp4, video_002.mp4, etc)

    nome_video_saida = gerar_proximo_nome_video()

    print(f"   -> Arquivo de saída: {nome_video_saida}")



    # OTIMIZAÇÃO DE RENDERIZAÇÃO PARA MÁXIMA VELOCIDADE

    # Usa configurações personalizáveis definidas no início do arquivo

    # threads=10 usa quase todos os 12 threads do Ryzen 5 8600G (deixa 2 livres para o sistema)

    # preset="faster" renderiza muito mais rápido que "medium" mantendo boa qualidade

    print(f"   -> Preset: {PRESET_RENDERIZACAO} | Threads: {THREADS_RENDERIZACAO}")

    video_final.write_videofile(

        nome_video_saida,

        fps=24,

        codec="libx264",

        audio_codec="libmp3lame",  # Codec MP3 para evitar dessincronia em vídeos longos

        audio_bitrate="192k",  # Garante qualidade do áudio

        preset=PRESET_RENDERIZACAO,  # Usa configuração do topo do arquivo

        threads=THREADS_RENDERIZACAO,  # Usa configuração do topo do arquivo

        temp_audiofile="temp_audio.mp3",  # Arquivo temporário para o áudio (MP3)

        remove_temp=True  # Remove arquivos temporários após renderização

    )

 

    # Fecha os clips para liberar memória

    video_final.close()

    audio_clip.close()

    for clip in clips_finais:

        clip.close()



    print(f"\n✅✅ VÍDEO LONGO PRONTO: {nome_video_saida}")

    print(f"🎬 Duração: {tempo_total/60:.2f} minutos")

    print(f"🔊 Áudio: Incluído e sincronizado!")

    print(f"📁 Salvo em: {PASTA_VIDEOS}/")



    # 6. UPLOAD PARA YOUTUBE (OPCIONAL)

    if FAZER_UPLOAD_YOUTUBE:

        print("\n" + "="*60)

        print("📺 UPLOAD PARA YOUTUBE")

        print("="*60)



        # Lê o texto da história para gerar metadados

        with open(ARQUIVO_TEXTO, "r", encoding="utf-8") as f:

            texto_completo = f.read()



        # Gera título e descrição com Gemini

        print("\n🤖 Gerando título e descrição com Gemini AI...")

        metadados = gerar_titulo_descricao_gemini(texto_completo)



        # Faz upload

        video_url = fazer_upload_youtube(

            nome_video_saida,

            metadados["titulo"],

            metadados["descricao"]

        )



        if video_url:

            print(f"\n🎉 PROCESSO COMPLETO!")

            print(f"📹 Vídeo renderizado: {nome_video_saida}")

            print(f"🔗 YouTube: {video_url}")

        else:

            print("\n⚠️  Vídeo renderizado, mas upload falhou.")

            print(f"   Você pode fazer upload manual de: {nome_video_saida}")

    else:

        print("\n💡 Upload para YouTube desativado.")

        print(f"   Para ativar, mude FAZER_UPLOAD_YOUTUBE = True no código")



if __name__ == "__main__":

    asyncio.run(criar_video_longo())