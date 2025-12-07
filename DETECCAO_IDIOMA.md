# 🌍 DETECÇÃO AUTOMÁTICA DE IDIOMA - CANAL DARK

## ✨ NOVA FUNCIONALIDADE

O sistema agora **detecta automaticamente o idioma** do texto da história e usa a **voz nativa** correspondente!

Você pode escrever histórias em qualquer idioma, e o Edge-TTS usará a voz apropriada automaticamente.

---

## 🎯 COMO FUNCIONA

### **Processo Automático:**

1. Você escreve a história em `historia.txt` (em qualquer idioma)
2. O sistema detecta o idioma do bloco **=== HISTÓRIA ===**
3. Seleciona automaticamente a voz nativa daquele idioma
4. Gera o áudio com a voz correta

### **Exemplo:**

```
=== TÍTULO ===
The Haunted Mansion

=== DESCRIÇÃO ===
A terrifying story about...

=== HISTÓRIA ===
It was a dark and stormy night when Sarah arrived at the old mansion...
```

**Resultado:**
```
🎙️  2. Gerando narração (apenas do bloco HISTÓRIA)...
   -> Gerando áudio e detectando CTAs...
   🌍 Idioma detectado: en
   🎙️  Voz selecionada: en-US-GuyNeural
```

---

## 🗣️ IDIOMAS SUPORTADOS

O sistema suporta **27+ idiomas** com vozes nativas profissionais:

### **Principais Idiomas:**

| Idioma | Código | Voz Edge-TTS |
|--------|--------|--------------|
| **Português (Brasil)** | pt | pt-BR-AntonioNeural |
| **Inglês (EUA)** | en | en-US-GuyNeural |
| **Espanhol** | es | es-ES-AlvaroNeural |
| **Francês** | fr | fr-FR-HenriNeural |
| **Alemão** | de | de-DE-ConradNeural |
| **Italiano** | it | it-IT-DiegoNeural |
| **Russo** | ru | ru-RU-DmitryNeural |
| **Japonês** | ja | ja-JP-KeitaNeural |
| **Chinês (Mandarim)** | zh-cn | zh-CN-YunxiNeural |
| **Coreano** | ko | ko-KR-InJoonNeural |
| **Árabe** | ar | ar-SA-HamedNeural |
| **Hindi** | hi | hi-IN-MadhurNeural |

### **Outros Idiomas Suportados:**

- 🇳🇱 Holandês (nl)
- 🇵🇱 Polonês (pl)
- 🇹🇷 Turco (tr)
- 🇸🇪 Sueco (sv)
- 🇳🇴 Norueguês (no)
- 🇩🇰 Dinamarquês (da)
- 🇫🇮 Finlandês (fi)
- 🇬🇷 Grego (el)
- 🇨🇿 Tcheco (cs)
- 🇭🇺 Húngaro (hu)
- 🇷🇴 Romeno (ro)
- 🇹🇭 Tailandês (th)
- 🇻🇳 Vietnamita (vi)
- 🇮🇩 Indonésio (id)
- 🇹🇼 Chinês (Taiwan) (zh-tw)

---

## ⚙️ CONFIGURAÇÃO

### **Ativar/Desativar Detecção Automática**

Edite o arquivo `app.py` (linha 57):

```python
# Detecção Automática de Idioma
DETECTAR_IDIOMA_AUTOMATICO = True  # True = detecta | False = usa voz padrão
```

**Opções:**
- `True` (padrão): Detecta idioma automaticamente e usa voz nativa
- `False`: Sempre usa VOZ_PADRAO (PT-BR)

### **Alterar Voz Padrão**

Se a detecção falhar ou estiver desativada, usa esta voz (linha 60):

```python
# Voz padrão (usada se detecção falhar ou estiver desativada)
VOZ_PADRAO = "pt-BR-AntonioNeural"  # Voz masculina PT-BR profissional
```

**Outras opções para português:**
```python
VOZ_PADRAO = "pt-BR-FranciscaNeural"  # Feminino suave
VOZ_PADRAO = "pt-BR-BrendaNeural"     # Feminino jovem
VOZ_PADRAO = "pt-BR-DonatoNeural"     # Masculino grave
```

### **Personalizar Vozes por Idioma**

Você pode alterar qual voz é usada para cada idioma editando o dicionário `VOZES_POR_IDIOMA` (linhas 63-142):

```python
VOZES_POR_IDIOMA = {
    'en': "en-US-GuyNeural",          # Mude para en-GB-RyanNeural (inglês britânico)
    'es': "es-MX-JorgeNeural",        # Mude para espanhol mexicano
    # ... outros idiomas
}
```

---

## 📦 INSTALAÇÃO DA BIBLIOTECA

### **Instalar langdetect:**

```bash
pip install langdetect
```

### **Se NÃO instalar:**

O sistema funciona normalmente, mas **sempre usará VOZ_PADRAO** (PT-BR).

Você verá este aviso:
```
⚠️  Biblioteca 'langdetect' não instalada. Instale com: pip install langdetect
   Usando PT-BR como idioma padrão.
```

---

## 📊 EXEMPLOS DE USO

### **Exemplo 1: História em Inglês**

**historia.txt:**
```
=== TÍTULO ===
The Midnight Visitor

=== DESCRIÇÃO ===
A chilling tale of horror...

=== HISTÓRIA ===
The old house stood silent in the moonlight. Nobody had lived there for decades...
```

**Resultado no Console:**
```
🎙️  2. Gerando narração (apenas do bloco HISTÓRIA)...
   -> Gerando áudio e detectando CTAs...
   🌍 Idioma detectado: en
   🎙️  Voz selecionada: en-US-GuyNeural
   ✅ Duração Total do Áudio: 2.50 minutos (150s)
```

### **Exemplo 2: História em Espanhol**

**historia.txt:**
```
=== TÍTULO ===
La Casa del Terror

=== DESCRIÇÃO ===
Una historia aterradora sobre...

=== HISTÓRIA ===
Era una noche oscura cuando María llegó a la casa abandonada...
```

**Resultado no Console:**
```
🎙️  2. Gerando narração (apenas do bloco HISTÓRIA)...
   -> Gerando áudio e detectando CTAs...
   🌍 Idioma detectado: es
   🎙️  Voz selecionada: es-ES-AlvaroNeural
   ✅ Duração Total do Áudio: 3.20 minutos (192s)
```

### **Exemplo 3: História em Japonês**

**historia.txt:**
```
=== TÍTULO ===
呪われた屋敷

=== DESCRIÇÃO ===
恐怖の物語...

=== HISTÓRIA ===
ある暗い夜、太郎は古い屋敷に到着した...
```

**Resultado no Console:**
```
🎙️  2. Gerando narração (apenas do bloco HISTÓRIA)...
   -> Gerando áudio e detectando CTAs...
   🌍 Idioma detectado: ja
   🎙️  Voz selecionada: ja-JP-KeitaNeural
   ✅ Duração Total do Áudio: 2.80 minutos (168s)
```

---

## 🐛 RESOLUÇÃO DE PROBLEMAS

### **Problema 1: Idioma Detectado Errado**

**Sintoma:**
```
🌍 Idioma detectado: fr
🎙️  Voz selecionada: fr-FR-HenriNeural
```
(Mas você escreveu em português)

**Causas:**
- Texto muito curto (menos de 50 caracteres)
- Texto com muitas palavras estrangeiras
- Texto misturado (português + inglês)

**Solução 1 - Desativar detecção:**
```python
DETECTAR_IDIOMA_AUTOMATICO = False  # Sempre usa PT-BR
```

**Solução 2 - Especificar voz manualmente:**
Edite temporariamente o código para forçar uma voz:
```python
# No arquivo app.py, linha 316 e 684, substitua:
voz_selecionada = detectar_idioma_texto(historia)
# Por:
voz_selecionada = "pt-BR-AntonioNeural"  # Força PT-BR
```

### **Problema 2: Biblioteca langdetect Não Instalada**

**Sintoma:**
```
⚠️  Biblioteca 'langdetect' não instalada.
   Usando PT-BR como idioma padrão.
```

**Solução:**
```bash
pip install langdetect
```

Se o pip não funcionar:
```bash
pip3 install langdetect
# ou
python -m pip install langdetect
```

### **Problema 3: Erro "Error loading langdetect"**

**Sintoma:**
```
⚠️  Erro na detecção de idioma: [Errno...]
🎙️  Usando voz padrão: pt-BR-AntonioNeural
```

**Solução:**
O sistema automaticamente usa a voz padrão. Isso não impede a geração do vídeo.

Se quiser corrigir:
```bash
pip uninstall langdetect
pip install langdetect
```

---

## ⚡ COMPORTAMENTO PADRÃO

### **Se langdetect INSTALADA:**
```
✅ Detecta idioma automaticamente
✅ Usa voz nativa do idioma
✅ Fallback para VOZ_PADRAO se falhar
```

### **Se langdetect NÃO INSTALADA:**
```
⚠️  Mostra aviso uma vez
✅ Usa VOZ_PADRAO sempre (PT-BR)
✅ Sistema funciona normalmente
```

### **Se DETECTAR_IDIOMA_AUTOMATICO = False:**
```
✅ Pula detecção completamente
✅ Usa VOZ_PADRAO sempre
✅ Mais rápido (economia de ~0.5s)
```

---

## 🎯 CASOS DE USO

### **Canal Multilíngue:**

Se você quer criar vídeos em vários idiomas, deixe ativado:
```python
DETECTAR_IDIOMA_AUTOMATICO = True
```

Basta escrever a história no idioma desejado!

### **Canal Apenas Português:**

Se você só faz vídeos em PT-BR, desative para economizar processamento:
```python
DETECTAR_IDIOMA_AUTOMATICO = False
VOZ_PADRAO = "pt-BR-AntonioNeural"
```

### **Testar Vozes Diferentes:**

Para testar vozes, desative a detecção e mude VOZ_PADRAO:
```python
DETECTAR_IDIOMA_AUTOMATICO = False
VOZ_PADRAO = "en-US-GuyNeural"  # Testa voz em inglês
```

---

## 📚 LISTA COMPLETA DE VOZES

Veja todas as vozes disponíveis em:
https://speech.microsoft.com/portal/voicegallery

**Como adicionar nova voz:**

1. Encontre o nome da voz no site (ex: "es-MX-JorgeNeural")
2. Adicione ao dicionário VOZES_POR_IDIOMA:

```python
VOZES_POR_IDIOMA = {
    # ... vozes existentes ...
    'es': "es-MX-JorgeNeural",  # Espanhol mexicano
}
```

---

## 🔧 CÓDIGO TÉCNICO

### **Função de Detecção:**

```python
def detectar_idioma_texto(texto):
    """
    Detecta o idioma do texto e retorna a voz nativa correspondente.
    """
    if not DETECTAR_IDIOMA_AUTOMATICO or not LANGDETECT_DISPONIVEL:
        return VOZ_PADRAO

    try:
        idioma_detectado = detect(texto)
        voz = VOZES_POR_IDIOMA.get(idioma_detectado, VOZ_PADRAO)
        print(f"   🌍 Idioma detectado: {idioma_detectado}")
        print(f"   🎙️  Voz selecionada: {voz}")
        return voz
    except Exception as e:
        print(f"   ⚠️  Erro na detecção: {e}")
        return VOZ_PADRAO
```

### **Integração:**

A função é chamada automaticamente em 2 lugares:

1. **Com CTA ativado** (linha 316):
```python
voz_selecionada = detectar_idioma_texto(texto)
comunicacao = edge_tts.Communicate(texto, voz_selecionada)
```

2. **Sem CTA** (linha 684):
```python
voz_selecionada = detectar_idioma_texto(historia)
comunicacao = edge_tts.Communicate(historia, voz_selecionada)
```

---

## ✅ CHECKLIST

Antes de usar a detecção de idioma:

- [ ] Instalei langdetect: `pip install langdetect`
- [ ] DETECTAR_IDIOMA_AUTOMATICO = True (padrão)
- [ ] Escrevi a história completamente em UM idioma
- [ ] Testei com `python app.py`
- [ ] Verifiquei no console qual idioma foi detectado

---

## 🎉 RESUMO

**ANTES:**
- ❌ Só funcionava em PT-BR
- ❌ Para mudar idioma, tinha que editar código
- ❌ Voz fixa

**AGORA:**
- ✅ **27+ idiomas suportados automaticamente**
- ✅ **Detecção automática de idioma**
- ✅ **Voz nativa para cada idioma**
- ✅ **Fallback inteligente se falhar**
- ✅ **Zero configuração necessária**

**Escreva em qualquer idioma e o sistema faz o resto! 🚀**
