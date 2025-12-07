# 🎯 GUIA: Como Fazer Upload para Canais Diferentes no Mesmo Email

Você tem **2 canais** no mesmo email do YouTube:
- 🇧🇷 **Canal Português** (lésbico)
- 🇮🇹 **Canal Italiano**

Os códigos agora usam **tokens separados** para cada canal!

---

## 🔑 COMO FUNCIONAM OS TOKENS

Cada script agora usa um arquivo de token diferente:

- `app.py` (português) → **`token_canal_portugues.pickle`**
- `app_italiano.py` (italiano) → **`token_canal_italiano.pickle`**

Quando você roda cada script pela **primeira vez**, ele vai:
1. Abrir o navegador
2. Pedir pra você fazer login no Google
3. **IMPORTANTE:** Pedir pra você **SELECIONAR QUAL CANAL** usar
4. Salvar essa escolha no token

Depois disso, o script sempre vai usar o canal que você escolheu!

---

## 📝 PASSO A PASSO: CONFIGURAR OS DOIS CANAIS

### **1️⃣ CONFIGURAR CANAL PORTUGUÊS (PRIMEIRO)**

```bash
# 1. Crie uma história em português
nano historia.txt

# 2. Execute o script português
python app.py
```

**O que vai acontecer:**
```
📤 Iniciando upload para YouTube...
```

1. Uma janela do navegador vai abrir
2. Faça login com seu email
3. **MUITO IMPORTANTE:** Aparecerá uma tela perguntando **"Qual canal você quer usar?"**
4. **Selecione o CANAL PORTUGUÊS (lésbico)**
5. Autorize o app
6. O token será salvo em `token_canal_portugues.pickle`

✅ A partir de agora, `app.py` sempre vai postar no canal português!

---

### **2️⃣ CONFIGURAR CANAL ITALIANO (DEPOIS)**

```bash
# 1. Crie uma história em italiano
nano storia_it.txt

# 2. Execute o script italiano
python app_italiano.py
```

**O que vai acontecer:**
```
📤 Iniziando upload su YouTube...
```

1. Uma janela do navegador vai abrir NOVAMENTE
2. Faça login com o **mesmo email**
3. **MUITO IMPORTANTE:** Aparecerá a tela **"Qual canal você quer usar?"**
4. **Selecione o CANAL ITALIANO**
5. Autorize o app
6. O token será salvo em `token_canal_italiano.pickle`

✅ A partir de agora, `app_italiano.py` sempre vai postar no canal italiano!

---

## 🎯 RESUMO

| Script | Token | Canal |
|--------|-------|-------|
| `app.py` | `token_canal_portugues.pickle` | 🇧🇷 Canal Português |
| `app_italiano.py` | `token_canal_italiano.pickle` | 🇮🇹 Canal Italiano |

**Cada token lembra qual canal você escolheu!**

---

## ⚠️ PROBLEMAS COMUNS

### **1. "Postou no canal errado!"**

**Solução:** Delete o token e refaça:

```bash
# Se postou português no canal errado:
rm token_canal_portugues.pickle
python app.py
# (selecione o canal correto desta vez)

# Se postou italiano no canal errado:
rm token_canal_italiano.pickle
python app_italiano.py
# (selecione o canal correto desta vez)
```

### **2. "Não apareceu a opção de escolher canal"**

Isso significa que você tem **apenas 1 canal** nesse email do YouTube.

**Como criar um segundo canal:**
1. Vá em https://studio.youtube.com
2. Clique no seu ícone de perfil (canto superior direito)
3. "Trocar conta" → "Ver todos os canais"
4. "Criar um canal"
5. Escolha "Usar um nome personalizado"
6. Nomeie o novo canal (ex: "Storie Italiane")
7. Pronto! Agora você tem 2 canais

Depois disso, ao rodar os scripts, a opção de escolher canal vai aparecer!

### **3. "Como ver qual canal está configurado?"**

Rode o script uma vez e veja a mensagem final:

```
✅ VÍDEO ENVIADO COM SUCESSO!
📝 Título: [seu título]
```

Depois vá no YouTube Studio e veja em qual canal o vídeo apareceu.

Se estiver errado, delete o token e refaça.

---

## 🔄 TROCAR DE CANAL (SE PRECISAR)

Se você quiser que um script poste em outro canal:

```bash
# Para trocar o canal do app.py:
rm token_canal_portugues.pickle
python app.py
# (escolha o outro canal quando aparecer)

# Para trocar o canal do app_italiano.py:
rm token_canal_italiano.pickle
python app_italiano.py
# (escolha o outro canal quando aparecer)
```

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

**Canal Português:**
- [ ] Tenho `client_secret.json` na pasta
- [ ] Criei `historia.txt`
- [ ] Rodei `python app.py`
- [ ] Autorizei e **selecionei canal PORTUGUÊS**
- [ ] Verifiquei no YouTube Studio que postou certo
- [ ] Arquivo `token_canal_portugues.pickle` foi criado

**Canal Italiano:**
- [ ] Criei as pastas (`intro_hailuo_it`, `background_loop_it`)
- [ ] Coloquei imagem em `background_loop_it/`
- [ ] Criei `storia_it.txt`
- [ ] Rodei `python app_italiano.py`
- [ ] Autorizei e **selecionei canal ITALIANO**
- [ ] Verifiquei no YouTube Studio que postou certo
- [ ] Arquivo `token_canal_italiano.pickle` foi criado

---

## 🎬 USO DIÁRIO (DEPOIS DE CONFIGURADO)

Depois que os tokens estão configurados, é só:

**Para postar em português:**
```bash
python app.py
```

**Para postar em italiano:**
```bash
python app_italiano.py
```

Cada um vai automaticamente pro canal correto! 🎯

---

## 🔒 SEGURANÇA

Os arquivos de token **NÃO** são enviados pro git (estão no `.gitignore`).

Eles ficam apenas no seu computador e contêm:
- Sua autorização para usar a API do YouTube
- A escolha de qual canal usar

**NUNCA compartilhe esses arquivos!**

---

## 💡 DICA PRO

Se você quiser **testar** sem fazer upload de verdade:

```python
# Em app.py ou app_italiano.py, linha 63/64:
FAZER_UPLOAD_YOUTUBE = False  # Só renderiza, não faz upload
```

Aí você pode renderizar o vídeo, ver se ficou bom, e só depois ativar o upload!

---

**Agora você está pronto para usar os dois canais sem misturar! 🚀**
