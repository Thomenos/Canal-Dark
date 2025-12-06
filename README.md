# 🎬 Canal Dark - Automação de Vídeos Longos para YouTube

Sistema automatizado de geração de vídeos de terror (dark content) de 40-60 minutos para YouTube, usando Python, síntese de voz neural e imagens/vídeos gerados por IA.

---

## 📋 Índice

- [Características](#-características)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Solução de Problemas](#-solução-de-problemas)
- [Perguntas Frequentes](#-perguntas-frequentes)

---

## ✨ Características

✅ **Vídeos Longos (40-60 min)** - Otimizado para narrativas extensas sem estourar memória RAM
✅ **Narração Neural Gratuita** - Usa Microsoft Edge TTS (voz Brian Multilingual)
✅ **Introdução Dinâmica** - Suporta vídeos curtos de IA (Hailuo, Runway, etc.)
✅ **Background Atmosférico** - Imagem estática de alta qualidade com loop infinito
✅ **Renderização Estável** - Codec otimizado para vídeos longos sem dessincronia
✅ **Zero Custos de API** - Todas as ferramentas usadas são gratuitas

---

## 🔧 Pré-requisitos

### Sistema Operacional
- Windows 10/11, Linux ou macOS

### Software Necessário

1. **Python 3.11** (⚠️ NÃO use Python 3.14 Alpha - tem incompatibilidade!)
   - Download: https://www.python.org/downloads/

2. **FFmpeg** (para renderização de vídeo)
   - Windows: https://www.gyan.dev/ffmpeg/builds/
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

---

## 📦 Instalação

### Passo 1: Clone ou Baixe o Projeto

```bash
git clone https://github.com/seu-usuario/Canal-Dark.git
cd Canal-Dark
```

### Passo 2: Instale as Dependências Python

```bash
pip install -r requirements.txt
```

**Tempo estimado:** 2-5 minutos

---

## 🚀 Como Usar

### Modo Rápido (Para Iniciantes)

1. **Edite sua história** - Abra o arquivo `historia.txt` e escreva ou cole sua narrativa de terror

2. **Execute o script** - Abra o terminal na pasta do projeto e digite:
   ```bash
   python app.py
   ```

3. **Aguarde** - O processo leva de 10 a 30 minutos dependendo do tamanho da história

4. **Pronto!** - O vídeo final estará em `video_longo_final.mp4`

---

### Modo Avançado (Com Introdução de Vídeos)

Para vídeos mais profissionais, você pode adicionar uma intro com vídeos curtos de IA:

1. **Gere vídeos de intro** usando Hailuo AI ou similar:
   - Acesse: https://hailuo.ai/
   - Crie 2-4 vídeos curtos (5-10s cada) com tema de terror
   - Baixe os vídeos em formato `.mp4`

2. **Adicione à pasta de intro:**
   - Renomeie os vídeos como: `intro_01.mp4`, `intro_02.mp4`, etc.
   - Cole na pasta `videos_hailuo/`

3. **Execute normalmente:**
   ```bash
   python app.py
   ```

---

## 📁 Estrutura do Projeto

```
Canal-Dark/
│
├── app.py                    # Script principal (EXECUTAR ESTE)
├── historia.txt              # Sua narrativa (EDITE AQUI)
├── requirements.txt          # Dependências Python
│
├── videos_hailuo/            # [OPCIONAL] Vídeos curtos de intro
│   ├── LEIA-ME.txt          # Instruções detalhadas
│   └── intro_01.mp4         # (Adicione seus vídeos aqui)
│
├── background_loop/          # Imagem de fundo para o vídeo longo
│   └── bg_principal.jpg     # (Gerado automaticamente ou manual)
│
├── imagens_temp/             # Cache de imagens (criado automaticamente)
│
├── narracao_longa.mp3        # Áudio gerado (criado automaticamente)
└── video_longo_final.mp4     # VÍDEO FINAL (OUTPUT)
```

---

## 🎨 Personalização

### Alterar a Voz da Narração

Edite o arquivo `app.py` na linha 37:

```python
VOZ = "en-US-BrianMultilingualNeural"  # Voz atual
```

**Outras opções de voz:**
- `pt-BR-FranciscaNeural` (Feminina, Português BR)
- `pt-BR-AntonioNeural` (Masculina, Português BR)
- `en-US-GuyNeural` (Masculina, Inglês)
- `en-US-JennyNeural` (Feminina, Inglês)

Lista completa: https://speech.microsoft.com/portal/voicegallery

### Usar Imagem de Fundo Personalizada

Opção 1: **Deixe o script gerar automaticamente**
- Ao executar, o script perguntará o tema (ex: "floresta escura")
- Gerará via Pollinations AI

Opção 2: **Use sua própria imagem**
- Salve uma imagem como `bg_principal.jpg`
- Cole na pasta `background_loop/`
- Recomendado: 1920x1080px (Full HD)

---

## ❓ Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'moviepy'"

**Solução:**
```bash
pip install -r requirements.txt
```

---

### Erro: "FFmpeg not found"

**Solução (Windows):**
1. Baixe FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Extraia o arquivo ZIP
3. Adicione a pasta `bin` ao PATH do sistema

**Solução (Linux):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

---

### Áudio Mudo ou Dessincronizado

**Solução:** O código já está corrigido para usar `libmp3lame`. Se persistir:
- Delete o arquivo `narracao_longa.mp3`
- Execute o script novamente

---

### Vídeo Muito Pesado (Mais de 500MB)

**Solução:** Ajuste a qualidade na linha 355 de `app.py`:

```python
preset="medium",  # Mude para "fast" ou "veryfast"
```

Opções: `ultrafast`, `veryfast`, `fast`, `medium`, `slow`
- Mais rápido = Arquivo maior e menor qualidade
- Mais lento = Arquivo menor e maior qualidade

---

## 💡 Perguntas Frequentes

### Quanto tempo demora para gerar um vídeo de 1 hora?

**Resposta:** Depende do seu computador:
- PC Moderno (i5/Ryzen 5): 15-25 minutos
- PC Antigo: 40-60 minutos
- A geração de áudio leva apenas 2-3 minutos
- O gargalo é a renderização de vídeo

---

### Posso usar histórias em Português?

**Sim!** Basta:
1. Escrever em português no `historia.txt`
2. Mudar a voz para `pt-BR-FranciscaNeural` ou `pt-BR-AntonioNeural`

---

### O script funciona sem a pasta videos_hailuo?

**Sim!** Se a pasta estiver vazia ou não existir:
- O vídeo começará direto com o background estático
- A qualidade será menor (sem intro impactante)
- Funcional para testes ou vídeos simples

---

### Posso gerar várias histórias sem reinstalar tudo?

**Sim!** Workflow recomendado:
1. Edite `historia.txt` com nova história
2. Delete o arquivo `narracao_longa.mp3` (para regerar áudio)
3. Execute `python app.py` novamente
4. (Opcional) Renomeie `video_longo_final.mp4` antes de rodar

---

### Como fazer vídeos de 2+ horas?

**Possível, mas não recomendado:**
- YouTube favorece vídeos de 40-60 minutos
- Renderização pode travar em PCs fracos
- Se necessário, basta escrever uma história maior

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique se instalou Python 3.11 (não 3.14!)
2. Certifique-se que FFmpeg está no PATH
3. Delete arquivos temporários e tente novamente:
   ```bash
   rm narracao_longa.mp3 video_longo_final.mp4
   python app.py
   ```

---

## 📜 Licença

Projeto de código aberto para fins educacionais.

**Aviso:** Respeite direitos autorais ao usar conteúdo gerado por IA no YouTube. Sempre adicione disclaimers de que é conteúdo gerado por IA quando necessário.

---

## 🎯 Roadmap Futuro

- [ ] Geração automática de legendas (SRT)
- [ ] Suporte a múltiplas vozes (diálogos)
- [ ] Interface gráfica (GUI) para não-programadores
- [ ] Efeitos de transição entre vídeos de intro
- [ ] Música de fundo atmosférica (royalty-free)

---

**Feito com ❤️ para criadores de conteúdo Dark no YouTube**
