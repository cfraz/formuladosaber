# Fórmula do Saber — Matemática Inteligente (MVP)

Protótipo Streamlit para Fundamental II: diagnóstico de 15 questões, relatório por assunto, exercícios personalizados e tutor opcional com Google Gemini.

## Requisitos
- Python 3.10 ou superior (recomendado 3.11/3.12)
- Chave da Gemini API para ativar o tutor (diagnóstico e exercícios funcionam sem chave)

## Executar no Windows
1. Instale Python em https://www.python.org/downloads/ e marque **Add Python to PATH**.
2. Extraia o ZIP e abra a pasta `formula_saber_mvp`.
3. Abra o Prompt de Comando nessa pasta.
4. Crie e ative o ambiente:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

5. Instale as dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Para ativar o tutor, crie `.streamlit/secrets.toml` com:

```toml
GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI"
```

Obtenha a chave em https://aistudio.google.com/app/apikey. **Não compartilhe a chave e não a envie ao GitHub.**

7. Inicie:

```powershell
streamlit run app.py
```

O navegador abrirá o endereço local indicado no terminal (normalmente http://localhost:8501).

## Publicar gratuitamente no Streamlit Community Cloud
1. Crie uma conta no GitHub e um repositório privado ou público para o projeto.
2. Envie os arquivos do projeto, mas NÃO envie `.streamlit/secrets.toml`.
3. Acesse https://share.streamlit.io/ e conecte o repositório.
4. Escolha `app.py` como arquivo principal.
5. Em **Advanced settings / Secrets**, adicione:

```toml
GEMINI_API_KEY = "SUA_CHAVE"
```

6. Clique em Deploy.

Consulte https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app e https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management.

## Estrutura

```text
formula_saber_mvp/
├── app.py
├── engine.py
├── tutor.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── questions.json
```

## Como funciona o diagnóstico
- 15 questões de múltipla escolha, distribuídas entre quatro assuntos.
- Correção feita localmente pelo Python, usando gabarito revisado no banco JSON.
- Resultado geral e percentual por assunto.
- Classificação: abaixo de 50% = precisa de reforço; 50% a 74% = em desenvolvimento; 75% ou mais = consolidado.
- O sistema sugere uma sequência de revisão com base nos resultados.

## Limitações conhecidas desta versão
- Os dados ficam na sessão do navegador/servidor e não constituem histórico permanente do aluno.
- O banco é pequeno e serve para piloto, não para avaliação escolar de alto impacto.
- O tutor faz chamadas ao Gemini e pode cometer erros; valide respostas antes de usar em contexto pedagógico.
- O MVP não tem login, pagamentos, painel administrativo ou controle de assinatura.
- Não solicite dados pessoais de crianças. Testes com menores devem ocorrer com ciência e acompanhamento dos responsáveis.

## Próximas melhorias
1. Aumentar e revisar o banco de questões por habilidade e série.
2. Incluir armazenamento persistente e autenticação com controle de acesso.
3. Adicionar painel do responsável e consentimentos/avisos adequados.
4. Medir custo de IA por sessão e aplicar limites de uso.
5. Criar checkout somente depois da validação com usuários reais.
