# TiCuida – Pré-triagem online e lotação de unidades de saúde

Projeto da disciplina **Programação Web Avançada – UVV**. O paciente faz uma pré-triagem antes de
sair de casa, recebe uma prioridade sugerida, vê as unidades que aceitam o seu convênio, ordenadas
por lotação e distância, e envia a triagem para a unidade escolhida ("Estou indo"). A unidade vê a
fila de quem está chegando e informa a própria lotação.

> O TiCuida **não faz diagnóstico** e não substitui atendimento médico. Em emergência, ligue **192**.

## Tecnologias

| Camada | Tecnologias |
|---|---|
| API REST | Python 3.12, Flask 3 (Application Factory + Blueprints), Flask-JWT-Extended, Flask-CORS |
| Validação | Pydantic 2 (validação no servidor, mensagens em português) |
| Persistência | Flask-SQLAlchemy 3 (`Mapped`/`mapped_column`), Flask-Migrate (Alembic), SQLite / PostgreSQL |
| Front-end | Vue 3, Vite, Vue Router, axios, Bulma 1 (mobile-first) |
| Qualidade | pytest + pytest-cov, black, flake8, invoke, logging com arquivo rotativo |

## Como rodar

Pré-requisitos: Python 3.12+ e Node.js 18+.

```bash
# 1. API (na raiz do projeto)
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev,test]"
copy .env.example .env            # Linux/macOS: cp .env.example .env
flask db upgrade                  # cria o banco (instance/ticuida.db)
flask seed                        # unidades, convênios, sintomas e contas de demonstração
flask run --debug                 # http://127.0.0.1:5000

# 2. Front-end (em outro terminal)
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Contas de demonstração (senha `Ticuida@2026`, configurável em `SEED_SENHA`):

- Paciente: `paciente@ticuida.dev`
- Operadores: `operador.<unidade>@ticuida.dev`. Exemplos: `operador.praiadacosta@ticuida.dev`,
  `operador.gloria@ticuida.dev`, `operador.itapua@ticuida.dev`, `operador.cobilandia@ticuida.dev`

### Testes e qualidade

```bash
pytest                                   # todos os testes
pytest tests/test_regras.py              # um arquivo
pytest tests/test_auth.py::test_login_com_sucesso   # um teste
pytest --cov=ticuida --cov-report=term-missing      # cobertura
flake8 ticuida tests && black --check ticuida tests
```

Com o invoke: `invoke install`, `invoke db`, `invoke seed`, `invoke run`, `invoke test --cov`, `invoke lint`.

## Arquitetura

Monólito modular: uma API Flask dividida em domínios e uma SPA Vue que consome a API.

```
ticuida/
├── __init__.py        create_app(): config → extensões → modelos → erros → blueprints
├── config.py          Config / TestConfig (variáveis do .env)
├── errors.py          APIError + handlers que sempre respondem JSON
├── seed.py            carga inicial idempotente (comando `flask seed`)
├── ext/               extensões, cada uma com init_app(app)
│   ├── db/            SQLAlchemy + convenção de nomes + register_models()
│   ├── migrate/  jwt_auth/  cors/  logs/  commands/
├── core/              /api/health, validação (Pydantic → 422), CPF, datas
├── auth/              cadastro, login, papéis (paciente/operador)
├── pacientes/         perfil do paciente
├── triagem/           sintomas, triagem e regras.py (prioridade, sem Flask/banco)
├── unidades/          unidades, convênios, lotação, recomendação (Haversine)
└── encaminhamentos/   "Estou indo", protocolo, fila e status
```

Cada domínio tem `models.py`, `schemas.py` (validação), `services.py` (regras de negócio e
consultas) e `routes.py` (blueprint fino). Documentação do MVP e do banco em `docs/`.

### Principais rotas

| Método | Rota | Quem |
|---|---|---|
| POST | `/api/auth/cadastro`, `/api/auth/login` | público |
| GET | `/api/auth/me` | logado |
| GET/PUT | `/api/pacientes/me` | paciente |
| GET | `/api/convenios`, `/api/sintomas` | público |
| POST/GET | `/api/triagens`, `/api/triagens/<id>` | paciente |
| GET | `/api/unidades?lat=&lng=&convenio_id=` | logado |
| POST | `/api/unidades/<id>/lotacao` | operador da unidade |
| POST | `/api/encaminhamentos` | paciente |
| GET | `/api/encaminhamentos/meus` | paciente |
| GET | `/api/encaminhamentos/fila?status=ativos\|todos` | operador |
| PATCH | `/api/encaminhamentos/<id>` | operador da unidade |
| GET | `/api/health` | público |

## Regras de prioridade (MVP 5.4)

| Prioridade | Critério |
|---|---|
| Emergência | qualquer sinal de alarme → orienta ligar 192 e interrompe o fluxo |
| Urgente | intensidade 7–10, febre > 39 °C, ou 60+ anos com sintomas há menos de 24 h |
| Pouco urgente | intensidade 4–6 ou febre (≥ 37,8 °C) até 39 °C |
| Não urgente | demais casos |
