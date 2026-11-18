import json
import os
from pathlib import Path

import streamlit as st

from engine import (
    classify_topic_scores,
    grade_assessment,
    make_study_plan,
    recommend_practice,
)
from tutor import ask_gemini

BASE_DIR = Path(__file__).parent
BANK_PATH = BASE_DIR / "data" / "questions.json"

st.set_page_config(
    page_title="Fórmula do Saber | Matemática Inteligente",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #F7F9F7; }
    [data-testid="stSidebar"] { background: #102B46; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .brand { color: #16865B; font-size: 2.0rem; font-weight: 800; margin-bottom: 0; }
    .subbrand { color: #173B5E; font-size: 1.05rem; font-weight: 650; margin-top: 0; }
    .small-note { color: #64748B; font-size: .85rem; }
    div[data-testid="stMetric"] { background: white; padding: 14px; border-radius: 12px; border: 1px solid #E4EAE5; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_bank():
    with BANK_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


BANK = load_bank()
DIAGNOSTIC = BANK["diagnostic"]
PRACTICE = BANK["practice"]
TOPIC_LABELS = BANK["topic_labels"]

if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None
if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []
if "practice_set" not in st.session_state:
    st.session_state.practice_set = []
if "practice_feedback" not in st.session_state:
    st.session_state.practice_feedback = None

st.sidebar.markdown("# 📐FÓRMULA DO SABER")
st.sidebar.caption("MATEMÁTICA INTELIGENTE")
st.sidebar.divider()
page = st.sidebar.radio(
    "Navegação",
    ["Início", "Diagnóstico", "Exercícios Personalizados", "Tutor com IA", "Meu resultado"],
)
st.sidebar.divider()
st.sidebar.caption("Versão Beta • Fundamental II")


def show_header():
    st.markdown('<p class="brand">FÓRMULA DO SABER</p>', unsafe_allow_html=True)
    st.markdown('<p class="subbrand">MATEMÁTICA INTELIGENTE</p>', unsafe_allow_html=True)


def eligible_questions(items, grade):
    return [q for q in items if q["year_min"] <= grade <= q["year_max"]]


show_header()

if page == "Início":
    st.title("Aprender Matemática começa por descobrir o que você já sabe.")
    st.write(
        "Faça um diagnóstico, descubra quais assuntos merecem atenção e pratique "
        "com atividades selecionadas para o seu nível escolar."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Questões diagnósticas", len(DIAGNOSTIC))
    c2.metric("Assuntos iniciais", len(TOPIC_LABELS))
    c3.metric("Etapas", "6º ao 9º ano")
    st.info("Comece pelo diagnóstico. Ele leva aproximadamente 10 a 15 minutos.")
    st.markdown("### O que você encontrará")
    a, b, c = st.columns(3)
    a.markdown("**🧭 Diagnóstico**\n\nIdentifique conteúdos que precisam de reforço.")
    b.markdown("**✏️ Prática personalizada**\n\nResolva atividades relacionadas aos seus resultados.")
    c.markdown("**🤖 Tutor com IA**\n\nPeça explicações e exemplos passo a passo.")
    st.caption("Este é um protótipo educacional. O resultado é orientativo e não substitui a avaliação do professor.")

elif page == "Diagnóstico":
    st.title("Diagnóstico de Matemática")
    st.write("Responda sem consultar o gabarito. Se não souber, escolha a alternativa que considerar mais provável.")
    grade = st.selectbox("Qual ano você está cursando?", [6, 7, 8, 9], format_func=lambda x: f"{x}º ano")
    questions = DIAGNOSTIC
    st.caption(f"{len(questions)} questões • Quatro áreas de conhecimento • Diagnóstico de conhecimentos fundamentais, não uma prova oficial do ano escolar")
    with st.form("diagnostic_form"):
        answers = {}
        for i, q in enumerate(questions, start=1):
            st.markdown(f"**Questão {i} — {TOPIC_LABELS[q['topic']]}**")
            st.write(q["question"])
            answers[q["id"]] = st.radio(
                "Escolha uma alternativa:",
                options=list(q["options"].keys()),
                format_func=lambda k, opts=q["options"]: f"{k}) {opts[k]}",
                key=f"diag_{q['id']}",
                index=None,
                label_visibility="collapsed",
            )
            st.divider()
        submitted = st.form_submit_button("Finalizar diagnóstico", type="primary", use_container_width=True)
    if submitted:
        unanswered = [qid for qid, value in answers.items() if value is None]
        if unanswered:
            st.error(f"Você ainda precisa responder {len(unanswered)} questão(ões).")
        else:
            result = grade_assessment(questions, answers)
            result["grade"] = grade
            result["topic_status"] = classify_topic_scores(result["topic_scores"])
            result["study_plan"] = make_study_plan(result["topic_scores"], TOPIC_LABELS)
            st.session_state.assessment_result = result
            st.session_state.practice_set = []
            st.success("Diagnóstico concluído! Acesse 'Meu resultado' para consultar sua análise.")
            st.rerun()

elif page == "Exercícios personalizados":
    st.title("Exercícios personalizados")
    result = st.session_state.assessment_result
    if not result:
        st.warning("Faça o diagnóstico antes de gerar sua prática personalizada.")
    else:
        weak_topics = [t for t, status in result["topic_status"].items() if status != "Consolidado"]
        if not weak_topics:
            weak_topics = list(TOPIC_LABELS.keys())
        st.write("Vamos praticar os assuntos que mais precisam de atenção.")
        selected_topic = st.selectbox(
            "Escolha um assunto",
            weak_topics,
            format_func=lambda t: TOPIC_LABELS[t],
        )
        if st.button("Gerar lista de exercícios", type="primary"):
            st.session_state.practice_set = recommend_practice(PRACTICE, selected_topic, result["grade"], limit=3)
            st.session_state.practice_feedback = None
        practice_set = st.session_state.practice_set
        if practice_set:
            with st.form("practice_form"):
                practice_answers = {}
                for i, q in enumerate(practice_set, start=1):
                    st.markdown(f"**Atividade {i}**")
                    st.write(q["question"])
                    practice_answers[q["id"]] = st.radio(
                        "Alternativa:", list(q["options"].keys()),
                        format_func=lambda k, opts=q["options"]: f"{k}) {opts[k]}",
                        key=f"practice_{q['id']}", index=None,
                        label_visibility="collapsed",
                    )
                check = st.form_submit_button("Corrigir atividades", type="primary")
            if check:
                if any(v is None for v in practice_answers.values()):
                    st.error("Responda todas as atividades antes de corrigir.")
                else:
                    st.session_state.practice_feedback = grade_assessment(practice_set, practice_answers)
                    st.rerun()
            feedback = st.session_state.practice_feedback
            if feedback:
                st.success(f"Você acertou {feedback['correct']} de {feedback['total']} atividades.")
                for q in practice_set:
                    st.markdown(f"**{q['question']}**")
                    st.write(f"Resposta correta: {q['answer']}. {q['explanation']}")

elif page == "Tutor com IA":
    st.title("Tutor de Matemática")
    st.write("Faça uma pergunta sobre Matemática. O tutor deve orientar o raciocínio, não apenas entregar a resposta.")
    result = st.session_state.assessment_result
    context = ""
    if result:
        context = "Resultados do diagnóstico: " + "; ".join(
            f"{TOPIC_LABELS[t]}: {score}% ({result['topic_status'][t]})"
            for t, score in result["topic_scores"].items()
        )
    for msg in st.session_state.tutor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ex.: Como resolvo uma equação do primeiro grau?")
    if prompt:
        st.session_state.tutor_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Preparando uma explicação..."):
                response = ask_gemini(prompt, context)
            st.markdown(response)
        st.session_state.tutor_messages.append({"role": "assistant", "content": response})
    try:
        gemini_configured = bool(os.getenv("GEMINI_API_KEY")) or bool(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    if not gemini_configured:
        st.caption("O tutor com IA precisa de uma chave Gemini configurada. O diagnóstico e os exercícios funcionam sem ela.")

elif page == "Meu resultado":
    st.title("Meu resultado")
    result = st.session_state.assessment_result
    if not result:
        st.info("Seu resultado aparecerá aqui depois que você concluir o diagnóstico.")
    else:
        st.metric("Desempenho geral", f"{result['percentage']}%", f"{result['correct']} de {result['total']} acertos")
        st.markdown("### Desempenho por assunto")
        for topic, score in result["topic_scores"].items():
            st.write(f"**{TOPIC_LABELS[topic]} — {score}%** · {result['topic_status'][topic]}")
            st.progress(score / 100)
        st.markdown("### Seu plano inicial de estudos")
        for item in result["study_plan"]:
            st.markdown(f"- **{item['topic']}**: {item['recommendation']}")
        with st.expander("Ver explicações das questões"):
            for item in result["details"]:
                st.markdown(f"**Questão {item['number']} — {'Acertou' if item['correct'] else 'Precisa revisar'}**")
                st.write(item["explanation"])
        report = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button("Baixar meu relatório", report, file_name="meu_diagnostico_matematica.json", mime="application/json")

st.divider()
st.caption("Fórmula do Saber • Matemática Inteligente | Protótipo educacional. Para menores de idade, a utilização deve ocorrer com ciência e acompanhamento do responsável.")
