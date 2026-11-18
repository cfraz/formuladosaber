import os
import streamlit as st


def get_api_key():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return ""


def ask_gemini(question: str, student_context: str = "") -> str:
    api_key = get_api_key()
    if not api_key:
        return (
            "O tutor com IA ainda não está configurado. O diagnóstico e os exercícios continuam funcionando. "
            "Para ativar o tutor, configure GEMINI_API_KEY conforme o arquivo README."
        )
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        system_prompt = (
            "Você é o Tutor de Matemática do Fórmula do Saber, voltado a estudantes brasileiros do 6º ao 9º ano. "
            "Responda em português simples, respeitoso e adequado à idade. Ensine o raciocínio em etapas, "
            "faça uma pergunta orientadora quando isso ajudar, mostre um exemplo curto e termine com um exercício "
            "de prática. Não invente regras matemáticas. Se a pergunta estiver fora de Matemática escolar, explique "
            "gentilmente o escopo. Nunca solicite nome completo, endereço, telefone, escola ou outros dados pessoais. "
            "Se houver dúvida sobre um cálculo, mostre a verificação. Não substitua o professor."
        )
        prompt = f"{system_prompt}\n\nContexto pedagógico disponível: {student_context or 'Ainda não há diagnóstico.'}\n\nPergunta do estudante: {question}"
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        text = getattr(response, "text", None)
        return text.strip() if text else "Não consegui gerar uma resposta agora. Tente reformular sua pergunta."
    except Exception as exc:
        # Não expor detalhes técnicos nem chaves ao estudante.
        return "Não foi possível acessar o tutor neste momento. Verifique a configuração da API ou tente novamente mais tarde."
