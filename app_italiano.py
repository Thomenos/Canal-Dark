"""
CANAL ITALIANO - Sistema de Automação de Vídeos para YouTube
Versão 2.0 - 100% OFFLINE - ITALIANO

Fluxo:
1. Lê arquivo storia_it.txt com formato específico (TÍTULO, DESCRIÇÃO, HISTÓRIA)
2. Gera narração em italiano apenas da parte HISTÓRIA
3. Monta vídeo com intro + background pulsante
4. Faz upload para YouTube com thumbnail
5. Limpa arquivos processados e arquiva storia_it.txt
"""

import asyncio
import edge_tts
import os
import glob
import shutil
from datetime import datetime
from moviepy.editor import (
    AudioFileClip, ImageClip, VideoFileClip,
    concatenate_videoclips, CompositeVideoClip
)
import cv2
import math

# Imports para YouTube Upload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle


# ============================================================================
# CONFIGURAÇÕES - CANAL ITALIANO
# ============================================================================

# Arquivos e Pastas (SEPARADOS DO CANAL EM PORTUGUÊS)
ARQUIVO_TEXTO = "storia_it.txt"
PASTA_ARQUIVADOS = "arquivados_it"
PASTA_VIDEOS = "videos_gerados_it"
PASTA_VIDEOS_INTRO = "intro_hailuo_it"  # Vídeos de intro (opcional)
PASTA_BACKGROUND = "background_loop_it"  # Imagem de fundo
NOME_AUDIO = "narracao_it_atual.mp3"

# Voz Edge-TTS (Italiano - Masculina Multilingual)
# Jorge Multilingual é uma voz que funciona bem com múltiplos idiomas
VOZ = "it-IT-DiegoNeural"  # Voz Diego - Masculino italiano (ou use "MultilingualNeural" se disponível)

# GIF de Call-to-Action (italiano)
GIF_INSCRICAO = "inscricao_it.gif"
ATIVAR_GIF_CTA = True

# Efeito de Pulso no Background
ATIVAR_EFEITO_PULSO = True

# Renderização
PRESET_RENDERIZACAO = "ultrafast"
THREADS_RENDERIZACAO = 12
RESOLUCAO_ALTURA = 720
RESOLUCAO_LARGURA = 1280

# YouTube Upload
FAZER_UPLOAD_YOUTUBE = True
ARQUIVO_CREDENCIAIS_YOUTUBE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


# ============================================================================
# FUNÇÕES DE PARSING
# ============================================================================

def parse_storia_txt(caminho_arquivo):
    """
    Lê e valida o arquivo storia_it.txt com formato específico.

    Formato esperado:
    === TÍTULO ===
    [Título do vídeo]

    === DESCRIÇÃO ===
    [Descrição do vídeo]

    === HISTÓRIA ===
    [História para narração em italiano]

    Returns:
        dict: {'titulo': str, 'descricao': str, 'historia': str}

    Raises:
        ValueError: Se o formato estiver incorreto
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(
            f"❌ Arquivo '{caminho_arquivo}' não encontrado!\n"
            f"   Crie o arquivo com o formato correto.\n"
            f"   Veja 'storia_ESEMPIO.txt' para referência."
        )

    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Verifica marcadores obrigatórios
    marcadores_necessarios = ['=== TÍTULO ===', '=== DESCRIÇÃO ===', '=== HISTÓRIA ===']
    for marcador in marcadores_necessarios:
        if marcador not in conteudo:
            raise ValueError(
                f"❌ ERRO DE FORMATO!\n\n"
                f"   O arquivo '{caminho_arquivo}' deve conter os 3 marcadores:\n"
                f"   - === TÍTULO ===\n"
                f"   - === DESCRIÇÃO ===\n"
                f"   - === HISTÓRIA ===\n\n"
                f"   Marcador faltando: {marcador}\n\n"
                f"   Veja o arquivo 'storia_ESEMPIO.txt' para o formato correto."
            )

    # Extrai blocos
    try:
        # Divide por marcadores
        partes = conteudo.split('=== TÍTULO ===')
        if len(partes) < 2:
            raise ValueError("Marcador === TÍTULO === não encontrado corretamente")
        resto = partes[1]

        partes = resto.split('=== DESCRIÇÃO ===')
        if len(partes) < 2:
            raise ValueError("Marcador === DESCRIÇÃO === não encontrado corretamente")
        titulo = partes[0].strip()
        resto = partes[1]

        partes = resto.split('=== HISTÓRIA ===')
        if len(partes) < 2:
            raise ValueError("Marcador === HISTÓRIA === não encontrado corretamente")
        descricao = partes[0].strip()
        historia = partes[1].strip()

        # Validação
        if not titulo:
            raise ValueError("❌ O bloco TÍTULO está vazio!")
        if not descricao:
            raise ValueError("❌ O bloco DESCRIÇÃO está vazio!")
        if not historia:
            raise ValueError("❌ O bloco HISTÓRIA está vazio!")

        # Limita título ao limite do YouTube
        if len(titulo) > 100:
            print(f"⚠️  Título muito longo ({len(titulo)} caracteres). Cortando para 100...")
            titulo = titulo[:97] + "..."

        return {
            'titulo': titulo,
            'descricao': descricao,
            'historia': historia
        }

    except Exception as e:
        raise ValueError(
            f"❌ Erro ao processar arquivo:\n"
            f"   {str(e)}\n\n"
            f"   Verifique se o formato está correto.\n"
            f"   Veja 'storia_ESEMPIO.txt' para referência."
        )


# ============================================================================
# FUNÇÕES DE ÁUDIO
# ============================================================================

async def gerar_audio_com_timestamps(texto, arquivo_saida):
    """
    Gera áudio da narração em italiano e detecta timestamps de CTAs (iscriviti).

    Args:
        texto: Texto da história para narrar
        arquivo_saida: Caminho do arquivo MP3 de saída

    Returns:
        list: Lista de dicts com timestamps onde aparecem CTAs
    """
    print("   -> Gerando áudio em italiano e detectando CTAs...")

    # Palavras-chave para detectar CTA em italiano
    cta_palavras = ['iscriviti', 'iscriverti', 'iscrivetevi', 'iscrizione', 'iscrivete']

    # Detecta posições das CTAs no texto
    texto_lower = texto.lower()
    timestamps_cta = []

    for cta in cta_palavras:
        pos = 0
        while True:
            pos = texto_lower.find(cta, pos)
            if pos == -1:
                break

            # Calcula % de posição no texto
            porcentagem = pos / len(texto)
            timestamps_cta.append({
                'palavra': cta,
                'posicao': pos,
                'porcentagem': porcentagem
            })
            pos += len(cta)

    # Gera o áudio em italiano
    comunicacao = edge_tts.Communicate(texto, VOZ)
    await comunicacao.save(arquivo_saida)

    # Calcula duração do áudio
    audio_clip = AudioFileClip(arquivo_saida)
    duracao_total = audio_clip.duration
    audio_clip.close()

    # Converte % em timestamps reais
    timestamps_finais = []
    for cta_info in timestamps_cta:
        timestamp = cta_info['porcentagem'] * duracao_total
        cta_info['timestamp'] = timestamp
        timestamps_finais.append(cta_info)
        print(f"   ✅ CTA '{cta_info['palavra']}' em {timestamp:.1f}s ({cta_info['porcentagem']*100:.1f}% do vídeo)")

    if timestamps_finais:
        print(f"   ✅ Total de {len(timestamps_finais)} CTA(s) detectado(s)!")
    else:
        print("   ℹ️  Nenhum CTA detectado no texto.")

    return timestamps_finais


# ============================================================================
# FUNÇÕES DE VÍDEO
# ============================================================================

def efeito_pulso(clip, intensidade=0.03, velocidade=10):
    """
    Aplica efeito de pulso/respiração (zoom in/out suave) no clip.

    Args:
        clip: VideoClip ou ImageClip
        intensidade: Quanto o zoom varia (0.03 = 3%)
        velocidade: Velocidade do pulso (maior = mais rápido)

    Returns:
        VideoClip com efeito aplicado
    """
    def aplicar_zoom(get_frame, t):
        # Calcula fator de zoom baseado em função seno
        fator = 1 + intensidade * math.sin(2 * math.pi * t / velocidade)

        # Pega frame original
        frame = get_frame(t)

        # Aplica zoom com OpenCV
        h, w = frame.shape[:2]
        novo_h, novo_w = int(h * fator), int(w * fator)

        # Resize
        frame_zoom = cv2.resize(frame, (novo_w, novo_h))

        # Crop para tamanho original (centralizado)
        start_y = (novo_h - h) // 2
        start_x = (novo_w - w) // 2
        frame_final = frame_zoom[start_y:start_y+h, start_x:start_x+w]

        return frame_final

    return clip.fl(aplicar_zoom)


def adicionar_gif_cta(video_clip, timestamps, caminho_gif, duracao_gif=3.0):
    """
    Adiciona GIF de inscrição nos momentos de CTA.
    GIF aparece no CENTRO ABSOLUTO da tela.

    Args:
        video_clip: VideoClip principal
        timestamps: Lista de {'timestamp': float} indicando quando mostrar GIF
        caminho_gif: Caminho para o arquivo GIF
        duracao_gif: Duração de exibição do GIF em segundos

    Returns:
        CompositeVideoClip com GIFs sobrepostos
    """
    if not timestamps or not os.path.exists(caminho_gif):
        return video_clip

    try:
        print(f"   -> Adicionando GIF em {len(timestamps)} momento(s)...")

        # Carrega GIF
        gif_clip = VideoFileClip(caminho_gif, has_mask=True)

        # Redimensiona GIF para tamanho adequado (20% da largura do vídeo)
        largura_gif = int(RESOLUCAO_LARGURA * 0.2)
        gif_clip = gif_clip.resize(width=largura_gif)

        # Cria overlays para cada timestamp
        gif_overlays = []
        for i, cta_info in enumerate(timestamps):
            timestamp = cta_info['timestamp']

            # Define início e fim do GIF
            inicio = timestamp
            fim = min(timestamp + duracao_gif, video_clip.duration)

            # Cria clip do GIF com timing correto
            # CENTRO ABSOLUTO: ("center", "center")
            gif_momento = (gif_clip
                          .set_start(inicio)
                          .set_duration(fim - inicio)
                          .set_position(("center", "center")))

            gif_overlays.append(gif_momento)

        # Combina vídeo original com todos os GIFs
        video_com_gifs = CompositeVideoClip([video_clip] + gif_overlays)

        print(f"   ✅ {len(timestamps)} GIF(s) adicionado(s) com sucesso no CENTRO da tela!")
        return video_com_gifs

    except Exception as e:
        print(f"⚠️ Erro ao adicionar GIF: {e}")
        return video_clip


# ============================================================================
# FUNÇÕES DE YOUTUBE
# ============================================================================

def autenticar_youtube():
    """Autentica no YouTube usando OAuth2."""
    creds = None

    # Token específico para o canal italiano
    TOKEN_FILE = 'token_canal_italiano.pickle'

    # Verifica se já existe token salvo
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Se não há credenciais válidas, faz login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(ARQUIVO_CREDENCIAIS_YOUTUBE):
                print(f"❌ Arquivo {ARQUIVO_CREDENCIAIS_YOUTUBE} não encontrado!")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                ARQUIVO_CREDENCIAIS_YOUTUBE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva token para próxima vez
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def fazer_upload_youtube(caminho_video, titulo, descricao, caminho_thumbnail=None):
    """
    Faz upload de vídeo para o YouTube como PRIVADO.

    Args:
        caminho_video: Caminho do arquivo de vídeo
        titulo: Título do vídeo
        descricao: Descrição do vídeo
        caminho_thumbnail: Caminho da imagem de thumbnail (opcional)

    Returns:
        str: URL do vídeo no YouTube, ou None se falhar
    """
    try:
        print("\n📤 Iniziando upload su YouTube...")

        youtube = autenticar_youtube()
        if not youtube:
            return None

        # Metadados do vídeo (tags em italiano)
        body = {
            'snippet': {
                'title': titulo,
                'description': descricao,
                'tags': ['storie', 'italiano', 'horror', 'racconti', 'mistero', 'paura'],
                'categoryId': '24'  # Categoria: Entretenimento
            },
            'status': {
                'privacyStatus': 'private',  # PRIVADO por padrão
                'selfDeclaredMadeForKids': False
            }
        }

        # Faz upload
        media = MediaFileUpload(caminho_video, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        print("   -> Caricamento in corso... (Questo richiederà tempo)")

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   -> Upload: {progress}% completato", end='\r')

        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Upload de thumbnail (se fornecido)
        if caminho_thumbnail and os.path.exists(caminho_thumbnail):
            try:
                print("\n   -> Caricamento miniatura...")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(caminho_thumbnail)
                ).execute()
                print("   ✅ Miniatura caricata!")
            except Exception as e:
                print(f"   ⚠️  Errore durante il caricamento della miniatura: {e}")

        print(f"\n✅ VIDEO CARICATO CON SUCCESSO!")
        print(f"🔗 URL: {video_url}")
        print(f"🔒 Stato: PRIVATO (puoi renderlo pubblico dopo)")
        print(f"📝 Titolo: {titulo}")

        return video_url

    except Exception as e:
        print(f"\n❌ Errore durante l'upload: {e}")
        return None


# ============================================================================
# PROTOCOLO DE LIMPEZA
# ============================================================================

def arquivar_storia():
    """
    Arquiva o arquivo storia_it.txt após processamento bem-sucedido.
    Move para pasta 'arquivados_it' com timestamp.
    """
    if not os.path.exists(ARQUIVO_TEXTO):
        return

    # Cria pasta de arquivados se não existir
    if not os.path.exists(PASTA_ARQUIVADOS):
        os.makedirs(PASTA_ARQUIVADOS)
        print(f"   ✅ Pasta '{PASTA_ARQUIVADOS}' criada!")

    # Gera nome do arquivo arquivado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    novo_nome = f"storia_PROCESSATA_{timestamp}.txt"
    caminho_destino = os.path.join(PASTA_ARQUIVADOS, novo_nome)

    # Move arquivo
    shutil.move(ARQUIVO_TEXTO, caminho_destino)
    print(f"   📦 Storia archiviata: {caminho_destino}")


def limpar_arquivos_processados():
    """
    Limpa arquivos temporários após processamento bem-sucedido:
    - Deleta vídeos da pasta intro_hailuo_it
    - Deleta imagens da pasta background_loop_it
    """
    print("\n🧹 Iniziando pulizia file processati...")

    arquivos_deletados = 0

    # Limpa vídeos de intro
    if os.path.exists(PASTA_VIDEOS_INTRO):
        videos_intro = glob.glob(os.path.join(PASTA_VIDEOS_INTRO, "*.mp4"))
        for video in videos_intro:
            try:
                os.remove(video)
                print(f"   🗑️  Cancellato: {os.path.basename(video)}")
                arquivos_deletados += 1
            except Exception as e:
                print(f"   ⚠️  Errore durante la cancellazione di {os.path.basename(video)}: {e}")

    # Limpa imagens de background
    if os.path.exists(PASTA_BACKGROUND):
        imagens = glob.glob(os.path.join(PASTA_BACKGROUND, "*.*"))
        for img in imagens:
            # Só deleta imagens comuns
            if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                try:
                    os.remove(img)
                    print(f"   🗑️  Cancellato: {os.path.basename(img)}")
                    arquivos_deletados += 1
                except Exception as e:
                    print(f"   ⚠️  Errore durante la cancellazione di {os.path.basename(img)}: {e}")

    if arquivos_deletados > 0:
        print(f"   ✅ {arquivos_deletados} file cancellati")
    else:
        print("   ℹ️  Nessun file da cancellare")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

async def criar_video_longo():
    """
    Função principal que orquestra todo o processo de criação do vídeo italiano.
    """
    print("=" * 70)
    print("CANALE ITALIANO - GENERATORE VIDEO v2.0 (100% OFFLINE)")
    print("=" * 70)

    # ========================================================================
    # 1. LER E VALIDAR ARQUIVO
    # ========================================================================

    print(f"\n📖 1. Lettura file '{ARQUIVO_TEXTO}'...")

    try:
        dados = parse_storia_txt(ARQUIVO_TEXTO)
        titulo = dados['titulo']
        descricao = dados['descricao']
        historia = dados['historia']

        print(f"   ✅ Titolo: {titulo}")
        print(f"   ✅ Descrizione: {len(descricao)} caratteri")
        print(f"   ✅ Storia: {len(historia)} caratteri")

    except (FileNotFoundError, ValueError) as e:
        print(f"\n{e}")
        print("\n💡 SUGGERIMENTO: Vedi il file 'storia_ESEMPIO.txt' per il formato corretto.")
        return

    # ========================================================================
    # 2. GERAR ÁUDIO (APENAS DA HISTÓRIA)
    # ========================================================================

    print(f"\n🎙️  2. Generazione narrazione italiana (solo blocco STORIA)...")

    if ATIVAR_GIF_CTA:
        timestamps_cta = await gerar_audio_com_timestamps(historia, NOME_AUDIO)
    else:
        comunicacao = edge_tts.Communicate(historia, VOZ)
        await comunicacao.save(NOME_AUDIO)
        timestamps_cta = []

    # Carrega áudio para saber duração
    audio_clip = AudioFileClip(NOME_AUDIO)
    tempo_total = audio_clip.duration
    print(f"   ✅ Durata totale audio: {tempo_total/60:.2f} minuti ({tempo_total:.0f}s)")

    # ========================================================================
    # 3. PREPARAR INTRO (OPCIONAL)
    # ========================================================================

    print("\n🎥 3. Preparazione Introduzione...")

    lista_clips_intro = []
    tempo_intro = 0

    if os.path.exists(PASTA_VIDEOS_INTRO):
        videos = sorted([f for f in os.listdir(PASTA_VIDEOS_INTRO) if f.endswith(".mp4")])

        if videos:
            print(f"   📹 Trovati {len(videos)} video di introduzione")
            for v in videos:
                path = os.path.join(PASTA_VIDEOS_INTRO, v)
                try:
                    clip = VideoFileClip(path).without_audio().resize(height=RESOLUCAO_ALTURA)
                    clip = clip.crop(
                        x1=clip.w/2 - RESOLUCAO_LARGURA/2,
                        y1=0,
                        width=RESOLUCAO_LARGURA,
                        height=RESOLUCAO_ALTURA
                    )
                    lista_clips_intro.append(clip)
                    tempo_intro += clip.duration
                    print(f"   -> Intro aggiunta: {v} ({clip.duration:.1f}s)")
                except Exception as e:
                    print(f"   ⚠️  Errore nel video {v}: {e}")
        else:
            print("   ℹ️  Nessun video di introduzione trovato")
    else:
        print(f"   ℹ️  Cartella '{PASTA_VIDEOS_INTRO}' non esiste. Saltando intro.")

    # ========================================================================
    # 4. PREPARAR BACKGROUND
    # ========================================================================

    tempo_restante = tempo_total - tempo_intro
    clip_background = None
    caminho_thumbnail = None

    if tempo_restante > 0:
        print(f"\n🎨 4. Preparazione sfondo per {tempo_restante/60:.2f} minuti rimanenti...")

        # Procura imagem de background
        if not os.path.exists(PASTA_BACKGROUND):
            print(f"   ❌ ERRORE: Cartella '{PASTA_BACKGROUND}' non esiste!")
            print(f"   💡 Crea la cartella e inserisci un'immagine di sfondo (JPG/PNG)")
            audio_clip.close()
            return

        imagens = (glob.glob(os.path.join(PASTA_BACKGROUND, "*.jpg")) +
                  glob.glob(os.path.join(PASTA_BACKGROUND, "*.png")) +
                  glob.glob(os.path.join(PASTA_BACKGROUND, "*.jpeg")))

        if not imagens:
            print(f"   ❌ ERRORE: Nessuna immagine trovata in '{PASTA_BACKGROUND}'!")
            print(f"   💡 Inserisci un'immagine di sfondo (JPG/PNG) nella cartella '{PASTA_BACKGROUND}'")
            audio_clip.close()
            return

        caminho_bg = imagens[0]
        caminho_thumbnail = caminho_bg  # Usa background como thumbnail
        print(f"   ✅ Sfondo trovato: {os.path.basename(caminho_bg)}")

        # Cria clip de imagem
        img_clip = ImageClip(caminho_bg)
        clip_background = img_clip.set_duration(tempo_restante).resize(height=RESOLUCAO_ALTURA).set_fps(24)

        # Centraliza crop 16:9
        clip_background = clip_background.crop(
            x1=clip_background.w/2 - RESOLUCAO_LARGURA/2,
            y1=0,
            width=RESOLUCAO_LARGURA,
            height=RESOLUCAO_ALTURA
        )

        # Aplica efeito de pulso
        if ATIVAR_EFEITO_PULSO:
            print(f"   -> Applicazione effetto pulsazione atmosferico...")
            clip_background = efeito_pulso(clip_background, intensidade=0.03, velocidade=10)
            print(f"   ✅ Sfondo configurato: {tempo_restante:.1f}s (con effetto pulsazione)")
        else:
            print(f"   ✅ Sfondo configurato: {tempo_restante:.1f}s (statico)")

    # ========================================================================
    # 5. MONTAR VÍDEO
    # ========================================================================

    print(f"\n💾 5. Montaggio timeline...")

    # Concatena intro + background
    if lista_clips_intro and clip_background:
        print("   -> Concatenazione intro + sfondo...")
        video_final = concatenate_videoclips(lista_clips_intro + [clip_background])
    elif lista_clips_intro:
        print("   -> Usando solo intro (senza sfondo)...")
        video_final = concatenate_videoclips(lista_clips_intro)
    elif clip_background:
        print("   -> Usando solo sfondo (senza intro)...")
        video_final = clip_background
    else:
        print("   ❌ ERRORE: Nessun video da processare!")
        audio_clip.close()
        return

    print(f"   -> Durata video prima dell'aggiustamento: {video_final.duration:.1f}s")
    print(f"   -> Durata audio: {audio_clip.duration:.1f}s")

    # Ajusta vídeo para duração do áudio
    if video_final.duration < audio_clip.duration:
        print("   ⚠️  Video più corto dell'audio! Estensione...")
        video_final = video_final.set_duration(audio_clip.duration)
    elif video_final.duration > audio_clip.duration:
        print("   ⚠️  Video più lungo dell'audio! Taglio...")
        video_final = video_final.subclip(0, audio_clip.duration)

    # Aplica áudio
    print("   -> Applicazione audio al video...")
    video_final = video_final.set_audio(audio_clip)
    print("   ✅ Audio applicato con successo!")

    # ========================================================================
    # 6. ADICIONAR GIF DE INSCRIÇÃO
    # ========================================================================

    if ATIVAR_GIF_CTA and timestamps_cta:
        print(f"\n🎨 6. Aggiunta GIF iscrizione in {len(timestamps_cta)} momento/i...")
        video_final = adicionar_gif_cta(video_final, timestamps_cta, GIF_INSCRICAO)
        print(f"   -> Durata finale video: {video_final.duration:.1f}s")

    # ========================================================================
    # 7. RENDERIZAR
    # ========================================================================

    print(f"\n🚀 7. RENDERING (Ci vorrà tempo, vai a prendere un caffè)...")

    # Cria pasta de vídeos se não existir
    if not os.path.exists(PASTA_VIDEOS):
        os.makedirs(PASTA_VIDEOS)

    # Gera nome do arquivo (sequencial)
    videos_existentes = glob.glob(os.path.join(PASTA_VIDEOS, "video_*.mp4"))
    numero_proximo = len(videos_existentes) + 1
    nome_video_saida = f"video_{numero_proximo:03d}.mp4"
    caminho_video_saida = os.path.join(PASTA_VIDEOS, nome_video_saida)

    print(f"   -> File di output: {caminho_video_saida}")
    print(f"   -> Preset: {PRESET_RENDERIZACAO} | Thread: {THREADS_RENDERIZACAO}")

    # Parâmetros de renderização otimizados
    ffmpeg_params = [
        "-crf", "23",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p"
    ]

    # Renderiza
    video_final.write_videofile(
        caminho_video_saida,
        codec='libx264',
        audio_codec='aac',
        preset=PRESET_RENDERIZACAO,
        threads=THREADS_RENDERIZACAO,
        fps=24,
        ffmpeg_params=ffmpeg_params
    )

    print(f"\n✅✅ VIDEO PRONTO: {caminho_video_saida}")
    print(f"🎬 Durata: {video_final.duration/60:.2f} minuti")
    print(f"🔊 Audio: Incluso e sincronizzato!")
    print(f"📁 Salvato in: {PASTA_VIDEOS}/")

    # Libera memória
    video_final.close()
    audio_clip.close()

    # ========================================================================
    # 8. UPLOAD PARA YOUTUBE
    # ========================================================================

    video_url = None

    if FAZER_UPLOAD_YOUTUBE:
        print("\n" + "="*70)
        print("📺 UPLOAD SU YOUTUBE")
        print("="*70)

        video_url = fazer_upload_youtube(
            caminho_video_saida,
            titulo,
            descricao,
            caminho_thumbnail
        )

    # ========================================================================
    # 9. PROTOCOLO DE LIMPEZA
    # ========================================================================

    print("\n" + "="*70)
    print("🧹 PROTOCOLLO DI PULIZIA (FRESH START)")
    print("="*70)

    limpar_arquivos_processados()
    arquivar_storia()

    # ========================================================================
    # 10. RESUMO FINAL
    # ========================================================================

    print("\n" + "="*70)
    print("🎉 PROCESSO COMPLETATO!")
    print("="*70)
    print(f"📹 Video renderizzato: {caminho_video_saida}")
    if video_url:
        print(f"🔗 YouTube: {video_url}")
    print(f"📦 Storia archiviata in: {PASTA_ARQUIVADOS}/")
    print(f"🧹 File temporanei puliti")
    print("\n✅ Pronto per il prossimo video!")
    print("="*70)


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    asyncio.run(criar_video_longo())
