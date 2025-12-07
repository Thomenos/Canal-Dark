# 🇮🇹 CANAL ITALIANO - Gerador de Vídeos Automático

Sistema separado para criação de vídeos em **italiano** para YouTube.

---

## 📂 ESTRUTURA DE PASTAS (SEPARADA DO CANAL EM PORTUGUÊS)

```
Canal-Dark/
├── app_italiano.py              ← Script principal para italiano
├── storia_it.txt                ← Seu arquivo de história (você cria isso)
├── storia_ESEMPIO.txt           ← Exemplo de formato
│
├── intro_hailuo_it/             ← Vídeos de intro (opcional)
│   └── intro.mp4
│
├── background_loop_it/          ← Imagem de fundo
│   └── sfondo.jpg
│
├── inscricao_it.gif             ← GIF de "Iscriviti"
│
├── videos_gerados_it/           ← Vídeos prontos (criado automaticamente)
│   └── video_001.mp4
│
└── arquivados_it/               ← Histórias processadas (criado automaticamente)
    └── storia_PROCESSATA_20250101_120000.txt
```

---

## 🎙️ VOZ USADA

**Diego (it-IT-DiegoNeural)** - Voz masculina italiana natural

> **NOTA:** Se você quiser usar a voz "Jorge Multilingual", me avise o nome exato da voz no Edge-TTS e eu atualizo!

---

## 🚀 COMO USAR

### **1. Crie as pastas necessárias:**

```bash
mkdir intro_hailuo_it
mkdir background_loop_it
mkdir videos_gerados_it
mkdir arquivados_it
```

### **2. Prepare seus arquivos:**

- Coloque uma **imagem de fundo** em `background_loop_it/` (JPG ou PNG)
- (Opcional) Coloque vídeos de intro em `intro_hailuo_it/`
- (Opcional) Coloque o GIF "Iscriviti" como `inscricao_it.gif`

### **3. Crie sua história em italiano:**

Crie o arquivo `storia_it.txt` com este formato:

```
=== TÍTULO ===
Il Mistero della Vecchia Casa

=== DESCRIÇÃO ===
Una storia affascinante che ti lascerà senza fiato...
🔔 Iscriviti per altre storie!

=== HISTÓRIA ===
Era una notte buia e tempestosa quando Marco arrivò alla vecchia casa...

Se ti piace questa storia, iscriviti al canale!

La porta cigolò mentre Marco entrava nel corridoio buio...
```

### **4. Execute o script:**

```bash
python app_italiano.py
```

### **5. O que acontece:**

1. ✅ Lê `storia_it.txt`
2. ✅ Gera áudio em **italiano** com voz Diego
3. ✅ Detecta CTAs ("iscriviti", "iscriverti", etc)
4. ✅ Cria vídeo com intro + background pulsante
5. ✅ Adiciona GIF nos momentos de CTA
6. ✅ Renderiza vídeo em `videos_gerados_it/`
7. ✅ Faz upload para YouTube (privado)
8. ✅ Arquiva `storia_it.txt` em `arquivados_it/`
9. ✅ Limpa intro e background

---

## 🎨 PALAVRAS-CHAVE CTA (ITALIANO)

O sistema detecta automaticamente essas palavras em italiano:

- **iscriviti**
- **iscriverti**
- **iscrivetevi**
- **iscrizione**
- **iscrivete**

Quando detectadas, o GIF `inscricao_it.gif` aparece no centro da tela!

---

## 📺 UPLOAD YOUTUBE

### **Tags automáticas em italiano:**
```python
'tags': ['storie', 'italiano', 'horror', 'racconti', 'mistero', 'paura']
```

### **Vídeos são enviados como PRIVADO** por padrão.

Você pode torná-los públicos depois manualmente no YouTube Studio.

---

## 🔧 CONFIGURAÇÕES

Abra `app_italiano.py` e edite conforme necessário:

```python
# Voz italiana
VOZ = "it-IT-DiegoNeural"  # Mude aqui se quiser outra voz

# GIF de CTA
ATIVAR_GIF_CTA = True      # False = sem GIF

# Efeito de pulso no background
ATIVAR_EFEITO_PULSO = True # False = imagem estática

# Upload automático
FAZER_UPLOAD_YOUTUBE = True # False = só renderiza
```

---

## 🆚 DIFERENÇA DO CANAL EM PORTUGUÊS

| Item | Canal Português | Canal Italiano |
|------|----------------|----------------|
| **Script** | `app.py` | `app_italiano.py` |
| **Arquivo** | `historia.txt` | `storia_it.txt` |
| **Voz** | Manuela (PT-BR) | Diego (IT) |
| **Pastas** | `videos_gerados/` | `videos_gerados_it/` |
| **CTAs** | inscreva-se, etc | iscriviti, etc |
| **Tags YouTube** | terror, horror | storie, mistero |

---

## ✅ CHECKLIST ANTES DE RODAR

- [ ] Pastas criadas (`intro_hailuo_it/`, `background_loop_it/`)
- [ ] Imagem de fundo em `background_loop_it/`
- [ ] Arquivo `storia_it.txt` criado com formato correto
- [ ] (Opcional) GIF `inscricao_it.gif` na raiz
- [ ] (Opcional) Vídeos de intro em `intro_hailuo_it/`
- [ ] YouTube credentials (`client_secret.json`) configurado

---

## 🎯 EXEMPLO RÁPIDO

```bash
# 1. Crie as pastas
mkdir intro_hailuo_it background_loop_it

# 2. Copie uma imagem de fundo
cp minha_imagem.jpg background_loop_it/

# 3. Crie sua história
nano storia_it.txt
# (cole o conteúdo com os 3 marcadores)

# 4. Execute!
python app_italiano.py
```

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### **Erro: Arquivo 'storia_it.txt' não encontrado**
→ Crie o arquivo na raiz do projeto com os 3 marcadores obrigatórios

### **Erro: Pasta 'background_loop_it' não existe**
→ `mkdir background_loop_it` e coloque uma imagem lá

### **Voz em português em vez de italiano**
→ Verifique se VOZ = "it-IT-DiegoNeural" em `app_italiano.py`

### **Quer mudar a voz**
→ Edite linha 52 de `app_italiano.py`:
```python
VOZ = "it-IT-GiuseppeNeural"  # Outra voz masculina italiana
# ou
VOZ = "it-IT-ElsaNeural"      # Voz feminina italiana
```

---

## 🎤 VOZES ITALIANAS DISPONÍVEIS

Veja lista completa: https://speech.microsoft.com/portal/voicegallery

**Masculinas:**
- `it-IT-DiegoNeural` (atual)
- `it-IT-GiuseppeNeural`
- `it-IT-BenignoNeural`

**Femininas:**
- `it-IT-ElsaNeural`
- `it-IT-IsabellaNeural`
- `it-IT-PalmiraNeural`

---

## 📞 SUPORTE

Se precisar de ajuda, verifique:
1. Formato do `storia_it.txt` está correto?
2. Pastas existem e têm conteúdo?
3. Python e dependências instaladas?

---

**Buona fortuna con il tuo canale italiano! 🇮🇹🎬**
