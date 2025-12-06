import asyncio

import edge_tts

import os

import requests

import google.generativeai as genai

from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip

 

# --- ⚙️ CONFIGURAÇÕES ---

CHAVE_GEMINI = "COLE_SUA_CHAVE_AQUI" # Se for usar geração de texto automática

ARQUIVO_TEXTO = "historia.txt"

NOME_AUDIO = "narracao_longa.mp3"

NOME_VIDEO = "video_longo_final.mp4"

 

# Pastas

PASTA_VIDEOS_INTRO = "videos_hailuo" # Intro impactante

PASTA_BACKGROUND = "background_loop" # Pasta para o fundo do vídeo longo

 

# Voz (Brian para narrar 1 hora é cansativo? Talvez testar outras, mas o Brian é bom)

VOZ = "en-US-BrianMultilingualNeural"

 

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



async def criar_video_longo():

    print("--- INICIANDO MODO VÍDEO LONGO (40-60min) ---")

 

    # 1. ÁUDIO (O MAIS IMPORTANTE)

    print(f"\n📖 1. Verificando áudio...")

 

    # Se o áudio já existir e você não mudou o texto, ele usa o mesmo para economizar tempo

    if os.path.exists(NOME_AUDIO):

        print("   -> Arquivo de áudio já existe. Usando ele.")

    else:

        if not os.path.exists(ARQUIVO_TEXTO):

            print("❌ Crie o arquivo historia.txt com sua história longa!")

            return

 

        print("   -> Gerando narração longa (Isso pode demorar uns minutos)...")

        with open(ARQUIVO_TEXTO, "r", encoding="utf-8") as f:

            texto = f.read()

 

        comunicacao = edge_tts.Communicate(texto, VOZ)

        await comunicacao.save(NOME_AUDIO)

 

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

 

    print(f"   -> Duração final do vídeo: {video_final.duration:.1f}s")

 

    # 5. RENDERIZAÇÃO

    print("\n🚀 RENDERIZANDO (Isso vai demorar, vá tomar um café)...")

    print(f"   -> Arquivo de saída: {NOME_VIDEO}")

 

    # CORREÇÃO: Usar preset "medium" em vez de "ultrafast" para melhor qualidade e compatibilidade

    # threads=4 ajuda a usar mais núcleos do processador

    # bitrate de áudio 192k garante boa qualidade

    video_final.write_videofile(

        NOME_VIDEO,

        fps=24,

        codec="libx264",

        audio_codec="libmp3lame",  # Codec MP3 para evitar dessincronia em vídeos longos

        audio_bitrate="192k",  # Garante qualidade do áudio

        preset="medium",  # Melhor que "ultrafast" para compatibilidade

        threads=4,

        temp_audiofile="temp_audio.mp3",  # Arquivo temporário para o áudio (MP3)

        remove_temp=True  # Remove arquivos temporários após renderização

    )

 

    # Fecha os clips para liberar memória

    video_final.close()

    audio_clip.close()

    for clip in clips_finais:

        clip.close()

 

    print(f"\n✅✅ VÍDEO LONGO PRONTO: {NOME_VIDEO}")

    print(f"🎬 Duração: {tempo_total/60:.2f} minutos")

    print(f"🔊 Áudio: Incluído e sincronizado!")

 

if __name__ == "__main__":

    asyncio.run(criar_video_longo())