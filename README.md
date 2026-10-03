# Portfolio

Site pessoal para apresentar portfólio, currículo e informações profissionais de Guilherme Luiz. Visitantes podem conhecer projetos, baixar o CV, enviar mensagem de contato e conversar com um assistente de IA sobre experiência, tecnologias e projetos.

**Produção:** https://portfolio-git-main-guilhermelics-projects.vercel.app/

---

## Funcionalidades

| Área | O que faz |
|------|-----------|
| **Página principal** | Seções de apresentação, serviços, projetos, contato e sobre mim |
| **Internacionalização** | Interface em inglês (`en`) e português brasileiro (`pt-BR`), com detecção por cookie ou `Accept-Language` |
| **Download do CV** | Rota `/download/<filename>` serve arquivos da pasta `cv/` |
| **Formulário de contato** | Envia e-mail via Flask-Mail (SMTP Gmail) |
| **Chat com IA** | Widget flutuante que responde perguntas sobre o currículo via proxy server-side |

---

## Arquitetura

```text
Visitante (browser)
    │
    ├─ GET  /                    → Página estática (Flask + Jinja2)
    ├─ POST /                    → Formulário de contato (e-mail)
    ├─ GET  /download/<arquivo>  → Download do CV
    ├─ GET  /api/chat/status     → Quota de perguntas da sessão
    └─ POST /api/chat            → Proxy para o backend de IA
                                      │
                                      ▼
                               portfolioai (configurado via CHAT_API_URL)
                                      │
                                      ▼
                               Modelo LLM (Groq) + RAG sobre corpus do currículo
```

O browser **não** chama o backend de IA diretamente. O Flask em `app.py` encaminha a pergunta para a URL definida em `CHAT_API_URL`.

### Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3, Flask, Flask-Mail |
| Frontend | HTML, CSS, JavaScript (sem framework) |
| Deploy | Vercel (`@vercel/python`) |
| Testes | pytest, responses |
| Backend de IA | Repositório separado **portfolioai** (Micronaut/Java) |

---

## Chat com IA

### Fluxo

1. Visitante abre o widget (botão flutuante).
2. Na primeira abertura da sessão, o assistente exibe boas-vindas e chips de sugestão (não consumem quota).
3. Visitante envia uma pergunta (máx. 2000 caracteres).
4. O front-end chama `POST /api/chat` no mesmo domínio do portfólio.
5. O Flask valida a pergunta, verifica a quota da sessão e repassa para `CHAT_API_URL`.
6. A resposta (`answer`) é renderizada no painel com markdown subset seguro.

### Contrato do proxy (`/api/chat`)

**Request**

```http
POST /api/chat
Content-Type: application/json

{"question": "Quais tecnologias você domina?"}
```

**Response — sucesso (`200`)**

```json
{
  "answer": "- **Java** – Micronaut, Spring Boot\n- **Python** – Flask, Django",
  "remaining": 6
}
```

**Status da quota (`GET /api/chat/status`)**

```json
{
  "used": 1,
  "limit": 7,
  "remaining": 6
}
```

| Status | Quando |
|--------|--------|
| `400` | Pergunta vazia ou acima de 2000 caracteres |
| `429` | Limite de perguntas da sessão atingido |
| `504` | Timeout ao aguardar o backend de IA |
| `503` | Backend de IA indisponível ou resposta inválida |

### UX do widget

- Mensagem de boas-vindas e três chips de sugestão na primeira abertura.
- Aviso de cold start: a primeira resposta pode demorar até 1 minuto se o servidor de IA estiver inativo.
- Indicador de loading e botão de retry em erros recuperáveis.
- Contador de perguntas restantes na sessão.
- Interface traduzida (`static/locales/en.json`, `static/locales/pt-BR.json`).

### Renderização das respostas

O backend devolve `answer` como texto livre com convenções de markdown leve. O front-end converte em HTML seguro via `formatAssistantMessage()` em `static/chat.js` (paridade com `format_assistant_message.py`):

| Sintaxe em `answer` | Renderização |
|---------------------|--------------|
| `- item` | `<ul><li>` |
| `**texto**` | `<strong>` |
| URLs `https://...` | `<a target="_blank" rel="noopener noreferrer">` |
| `\n\n` | parágrafos `<p>` |
| Texto sem markdown | escapado, sem tags |

HTML do modelo é sempre escapado. Tabelas, fenced code e cabeçalhos `#` **não** são interpretados.

Detalhes completos do contrato HTTP e do formato de `answer`: [`chat-response-format.md`](chat-response-format.md).

### Limitações

| Limitação | Detalhe |
|-----------|---------|
| **Quota por sessão** | 7 perguntas (padrão; configurável via `CHAT_QUESTION_LIMIT`) |
| **Tamanho da pergunta** | Máximo 2000 caracteres |
| **Timeout** | 120 segundos no proxy e no Vercel (`maxDuration: 120` em `vercel.json`) |
| **Cold start** | Backend de IA em plano gratuito pode levar ~60 s após período de inatividade |
| **Sem streaming** | Resposta completa de uma vez; não há SSE |
| **Sem JSON estruturado** | Apenas campo `answer` (texto); sem `items[]` ou `blocks[]` |
| **Markdown parcial** | Só bullets, negrito, parágrafos e URLs; sem tabelas, imagens ou código fenced |
| **Respostas não determinísticas** | Mesma pergunta pode variar na redação |
| **Escopo do assistente** | Responde sobre o currículo; recusa perguntas fora de escopo |
| **Sugestões não consomem quota** | Chips preenchem o input; só o envio conta |

---

## Desenvolvimento local

### Pré-requisitos

- Python 3.10+
- Backend **portfolioai** rodando localmente (padrão: `http://localhost:8080/api/v1/chat`)

### Configuração

```bash
# Clonar e instalar dependências
pip install -r requirements.txt

# Criar .env na raiz do projeto
cat > .env <<'EOF'
CHAT_API_URL=http://localhost:8080/api/v1/chat
secret_key=dev-secret-change-me
senha_email=<senha-app-gmail>
EOF
```

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `CHAT_API_URL` | Não | `http://localhost:8080/api/v1/chat` | URL do endpoint de chat do portfolioai |
| `secret_key` | Sim (sessão Flask) | — | Chave secreta para cookies de sessão |
| `senha_email` | Sim (contato) | — | Senha de app Gmail para envio de e-mail |
| `CHAT_QUESTION_LIMIT` | Não | `7` | Perguntas por sessão |
| `CHAT_REQUEST_TIMEOUT` | Não | `120` | Timeout em segundos para o upstream |

### Executar

```bash
python app.py
```

Abra `http://localhost:5000` e teste o widget de chat.

### Testes

```bash
pytest
```

Principais suites:

| Arquivo | Cobre |
|---------|-------|
| `tests/test_chat_api.py` | Proxy `/api/chat`, quota, erros |
| `tests/test_format_assistant_message.py` | Parser markdown subset (Python) |
| `tests/test_linkify_urls.py` | Autolink seguro de URLs |
| `tests/test_chat_assets.py` | Contrato do `chat.js` |
| `tests/test_locales.py` | Paridade de chaves i18n |
| `tests/test_vercel_config.py` | `maxDuration` no `vercel.json` |
| `tests/test_chat_template.py` | Elementos do widget no template |

## Estrutura do projeto

```text
Portfolio/
├── app.py                      # Flask: rotas, proxy de chat, e-mail
├── locale_loader.py            # Carregamento de mensagens server-side
├── format_assistant_message.py # Parser markdown subset (Python)
├── linkify_urls.py             # Autolink seguro de URLs
├── templates/home.html         # Página principal + widget de chat
├── static/
│   ├── chat.js                 # Widget de chat (front-end)
│   ├── chat.css                # Estilos do chat
│   ├── i18n.js                 # Internacionalização client-side
│   ├── locales/                # Traduções en e pt-BR
│   ├── main.css                # Estilos da página
│   └── script.js               # Menu responsivo
├── cv/                         # Arquivos de currículo para download
├── tests/                      # Testes pytest
├── vercel.json                 # Configuração de deploy
└── chat-response-format.md     # Contrato detalhado do formato de resposta
```

---

## Referências

| Recurso | Link / arquivo |
|---------|----------------|
| Site em produção | https://portfolio-git-main-guilhermelics-projects.vercel.app/ |
| Modelo visual (Marnei Cardoso) | https://www.youtube.com/watch?v=mNu3Oc0OT7Q&list=PLDIbjIlhRaxNiOXcpnRUe1klzo0OO5kHO |
| Contrato de resposta do chat | [`chat-response-format.md`](chat-response-format.md) |
| Backend de IA | [Repositório **portfolioai** (Micronaut/Java, deploy Render)](https://github.com/guilhermeluizcosta/portfolioai) |
| LinkedIn | https://www.linkedin.com/in/guilherme-luiz-379704193/ |
| GitHub | https://github.com/guilhermeluizcosta/ |

---

## Créditos

Layout baseado no tutorial de [Marnei Cardoso](https://www.youtube.com/watch?v=mNu3Oc0OT7Q&list=PLDIbjIlhRaxNiOXcpnRUe1klzo0OO5kHO). Ícones via [Boxicons](https://boxicons.com/).
