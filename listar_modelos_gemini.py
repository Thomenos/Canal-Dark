"""
Script para listar todos os modelos Gemini disponíveis na sua conta.
Use para descobrir qual modelo usar no app.py
"""

import google.generativeai as genai

# Cole sua chave Gemini aqui (a mesma do app.py)
CHAVE_GEMINI = "COLE_SUA_CHAVE_AQUI"

print("🔍 LISTANDO MODELOS GEMINI DISPONÍVEIS...\n")
print("=" * 70)

try:
    genai.configure(api_key=CHAVE_GEMINI)

    print("\n📋 MODELOS DISPONÍVEIS:\n")

    for model in genai.list_models():
        # Filtra apenas modelos que suportam generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Descrição: {model.description[:100]}...")
            print(f"   Métodos suportados: {', '.join(model.supported_generation_methods)}")
            print()

    print("=" * 70)
    print("\n💡 COMO USAR:")
    print("   1. Copie o nome do modelo (ex: 'models/gemini-1.5-flash')")
    print("   2. No app.py, use SEM o prefixo 'models/':")
    print("      model = genai.GenerativeModel('gemini-1.5-flash')")
    print("\n✅ MODELOS RECOMENDADOS PARA SEU USO:")
    print("   - gemini-1.5-flash (rápido e barato)")
    print("   - gemini-1.5-pro (mais preciso)")
    print("   - gemini-2.0-flash-exp (experimental, mais recente)")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\n⚠️  POSSÍVEIS CAUSAS:")
    print("   1. Chave Gemini inválida ou não configurada")
    print("   2. Quota diária excedida (espere até amanhã)")
    print("   3. Sem conexão com internet")
    print("\n💡 SOLUÇÃO:")
    print("   - Abra este arquivo e cole sua chave na linha 8")
    print("   - Rode novamente: python listar_modelos_gemini.py")
