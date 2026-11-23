# TiCuida – Pré-triagem Online e Lotação de Unidades de Saúde

**Disciplina:** Programação Web Avançada – UVV
**Autor:** Bernardo Abaurre
**Versão:** 1.0 – descrição do MVP (2º bimestre)

## 1. Introdução e problema

Quem precisa de atendimento em um pronto-atendimento ou clínica normalmente passa por **duas filas**. A primeira é a da recepção e triagem, onde informa dados pessoais e queixas. A segunda é a da consulta médica. Além disso, o paciente sai de casa **sem saber se a unidade está lotada** ou se ela **atende o seu convênio**. O resultado é perda de tempo, deslocamentos desnecessários e superlotação concentrada em poucas unidades.

Do lado da unidade de saúde, a equipe só descobre quem está chegando, e com qual gravidade, quando o paciente já está na recepção. Isso impede qualquer preparo antecipado e sobrecarrega as primeiras etapas do atendimento.

O **TiCuida** propõe atacar esse problema levando a triagem para antes da chegada do paciente. Esta descrição define a versão inicial (MVP) da aplicação web, com escopo reduzido ao essencial.

## 2. Objetivos

**Objetivo geral:** desenvolver uma aplicação web que permita ao paciente fazer uma **pré-triagem online antes de sair de casa** e enviar esses dados para a unidade de saúde escolhida, reduzindo o tempo de espera e a lotação nas primeiras etapas do atendimento.

**Objetivos específicos:**

- Permitir que o paciente registre seus sintomas e dados de identificação pelo celular, de qualquer lugar.
- Sugerir um nível de prioridade a partir de regras simples e orientar casos de emergência ao SAMU (192).
- Indicar as unidades de saúde compatíveis com o convênio do paciente, ordenadas por lotação e distância.
- Enviar a pré-triagem para a unidade escolhida, para que a equipe se prepare antes da chegada.
- Dar à unidade uma visão da demanda que está a caminho e um meio simples de informar sua lotação.

## 3. Público-alvo

| Perfil | Descrição | Necessidade principal |
|---|---|---|
| Paciente (primário) | Adultos da Grande Vitória (piloto em Vila Velha/ES) que buscam pronto-atendimento ou clínica por queixas de baixa e média complexidade, com ou sem convênio. | Saber para onde ir, esperar menos e não repetir informações na recepção. |
| Operador da unidade (secundário) | Recepção e equipe de enfermagem de clínicas e prontos-atendimentos parceiros. | Saber quem está chegando, com qual prioridade, e divulgar a lotação atual. |

**Fora do público-alvo:** situações de emergência. Quando a triagem identifica um sinal de alarme, o sistema interrompe o fluxo e orienta o paciente a ligar para o **SAMU (192)** ou ir à emergência mais próxima.

## 4. Proposta de valor

> “O TiCuida é um sistema de triagem virtual que visa reduzir a lotação em centros médicos.”
- **Para o paciente:** escolhe a unidade certa antes de sair de casa, considerando convênio aceito, lotação e distância, e chega com os dados já preenchidos. Isso evita a fila da triagem presencial e o deslocamento até uma unidade cheia.
- **Para a unidade de saúde:** recebe a pré-triagem antes da chegada do paciente, com prioridade sugerida, e consegue se preparar. Ao publicar a própria lotação, também distribui melhor a demanda entre as unidades.
- **Diferencial:** reúne em **um único fluxo** três informações que hoje ficam separadas: triagem, lotação e convênio. Funciona no navegador do celular, sem instalar aplicativo.
- **Limite importante:** o TiCuida **não faz diagnóstico** e não substitui a avaliação profissional. A prioridade é apenas uma sugestão, calculada por regras simples inspiradas no Protocolo de Manchester, e a classificação oficial continua sendo feita pela equipe da unidade.

## 5. Funcionalidades do MVP (escopo)

As funcionalidades foram priorizadas pelo método **MoSCoW**. Só os itens **Must** são obrigatórios para considerar o MVP concluído.

### 5.1 Essenciais (Must)

| ID | Funcionalidade | Descrição | Perfil |
|---|---|---|---|
| F1 | Cadastro e login | Cadastro com dados mínimos (nome, CPF, data de nascimento, telefone, contato de emergência e convênio) e aceite do termo de consentimento. Login com e-mail e senha. | Paciente |
| F2 | Triagem online em etapas | Formulário em passos: (1) queixa principal e sintomas comuns; (2) sinais de alarme; (3) intensidade (escala 0–10) e há quanto tempo começou; (4) confirmação dos dados. | Paciente |
| F3 | Prioridade sugerida | Regras simples classificam a triagem em Emergência, Urgente, Pouco urgente ou Não urgente. Em caso de Emergência, aparece um alerta para ligar 192 e o fluxo é interrompido. | Paciente |
| F4 | Unidades recomendadas | Lista de unidades que aceitam o convênio do paciente (ou atendimento particular), ordenadas por lotação e distância. A distância é calculada pela localização do navegador. | Paciente |
| F5 | “Estou indo” | O paciente escolhe uma unidade e confirma. O sistema gera um protocolo e envia a pré-triagem para a fila da unidade. | Paciente |
| F6 | Fila da unidade | Painel com as pré-triagens enviadas para a unidade do operador, ordenadas por prioridade e horário. Status: a caminho → chegou → atendido, ou não compareceu. | Operador |
| F7 | Atualizar lotação | O operador informa a lotação atual (baixa, média ou alta). O paciente vê esse nível com a indicação “atualizado há X min”. | Operador |

### 5.2 Desejáveis (Should), se houver tempo

- Mapa com as unidades recomendadas (Leaflet + OpenStreetMap).
- Histórico de triagens e protocolos do paciente.
- Edição de perfil.
- Páginas estáticas “Sobre” e “FAQ”.

### 5.3 Fora do MVP (Won't)

- Agendamento de consultas e prontuário eletrônico.
- Integração com sistemas hospitalares ou de operadoras de convênio.
- Diagnóstico ou triagem por inteligência artificial.
- Aplicativo nativo, notificações push e atendimento via WhatsApp.
- Painel administrativo. As unidades, convênios e operadores serão cadastrados por script de carga inicial (seed).
- Recuperação de senha por e-mail.
- Coleta de dados pessoais além do necessário para a triagem (religião, cor/etnia, tipo sanguíneo, profissão etc.), seguindo o princípio da minimização de dados da LGPD.

### 5.4 Regras de prioridade (versão inicial)

| Prioridade | Critério (simplificado) | Ação do sistema |
|---|---|---|
| Emergência | Qualquer sinal de alarme: dor forte no peito, falta de ar intensa, desmaio, convulsão, sangramento intenso, confusão mental ou fraqueza súbita em um lado do corpo. | Interrompe o fluxo e orienta ligar 192 ou ir à emergência mais próxima. |
| Urgente | Dor com intensidade de 7 a 10, febre acima de 39 °C ou paciente com 60 anos ou mais e sintomas há menos de 24 h. | Recomenda unidades e destaca a prioridade na fila da unidade. |
| Pouco urgente | Dor com intensidade de 4 a 6 ou febre até 39 °C. | Recomenda unidades normalmente. |
| Não urgente | Demais casos (sintomas leves, intensidade de 0 a 3). | Recomenda unidades normalmente. |

As regras ficam em um módulo isolado do back-end, para serem revisadas e ajustadas por profissionais de saúde sem alterar o restante do sistema.

## 6. Fluxos principais

**Fluxo do paciente:**

1. Acessa o site pelo celular, cria a conta ou faz login.
2. Clica em “Iniciar triagem” e responde às etapas do formulário.
3. Recebe a prioridade sugerida. Se for Emergência, é orientado a ligar 192 e o fluxo termina.
4. Autoriza a localização e vê as unidades compatíveis com o seu convênio, com lotação e distância.
5. Escolhe uma unidade e clica em “Estou indo”.
6. Recebe a confirmação com o número de protocolo, que apresenta na recepção.

**Fluxo do operador da unidade:**

1. Faz login com a conta vinculada à sua unidade.
2. Vê a fila de pré-triagens a caminho, ordenada por prioridade.
3. Abre uma pré-triagem para ver sintomas e dados do paciente.
4. Atualiza o status (chegou, atendido ou não compareceu).
5. Sempre que a situação mudar, atualiza a lotação da unidade (baixa, média ou alta).

## 7. Requisitos não funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF1 | Privacidade (LGPD) | Dados de saúde são sensíveis. A coleta exige consentimento explícito, guarda só o mínimo necessário e cada operador acessa apenas as triagens enviadas para a sua unidade. |
| RNF2 | Segurança | Senhas armazenadas com hash (werkzeug.security). Autenticação por token e autorização por papel (paciente ou operador). Validação dos dados de entrada na API. |
| RNF3 | Usabilidade | Interface mobile-first e responsiva, com no máximo 4 etapas na triagem. O paciente deve concluir a triagem em até 3 minutos. |
| RNF4 | Aviso legal | Aviso visível em todas as telas da triagem de que o sistema não substitui atendimento médico, com o número 192 em destaque. |
| RNF5 | Desempenho | Respostas da API em menos de 2 segundos para as operações comuns, em ambiente de demonstração. |
| RNF6 | Acessibilidade | Contraste adequado, campos com rótulos (labels) e navegação por teclado nos formulários. |
| RNF7 | Manutenibilidade | Código organizado em módulos por domínio, Application Factory e testes automatizados (pytest) para as regras de prioridade e os endpoints principais. |
| RNF8 | Portabilidade | Configuração por variáveis de ambiente (.env). SQLite em desenvolvimento e PostgreSQL em produção sem alterar o código. |

## 8. Arquitetura e tecnologias (preliminar)

### 8.1 Visão geral

A aplicação será um **monólito modular**: um único back-end Flask, dividido internamente em módulos por domínio, e um front-end SPA separado que consome a API REST. Microsserviços foram descartados porque o MVP é desenvolvido por uma única pessoa, usa um único banco de dados e nenhuma parte com necessidade de escala independente, que são os critérios discutidos na Unidade 4. A modularização interna permite separar algum módulo no futuro, se for preciso.

| Camada | Responsabilidade | Tecnologias |
|---|---|---|
| Front-end (SPA) | Telas do paciente e do operador, formulário em etapas, geolocalização | Vue 3, Vite, Vue Router, axios, Leaflet (Should) |
| API REST | Rotas por domínio, autenticação, regras de prioridade e de recomendação | Python 3.12, Flask (Application Factory + Blueprints), Flask-CORS, Flask-JWT-Extended |
| Persistência | Modelos, migrações e acesso a dados | Flask-SQLAlchemy 3 (Mapped/mapped_column), Flask-Migrate |
| Banco de dados | Armazenamento | SQLite (desenvolvimento) e PostgreSQL (produção) |
| Ferramentas | Ambiente e qualidade | venv, pyproject.toml, invoke, pytest, Git/GitHub |

### 8.2 Organização do back-end

Segue a estrutura do projeto TaskFlow visto em aula: `create_app()` em `ticuida/__init__.py`, extensões em `ticuida/ext/` com `init_app`, e um pacote por domínio, cada um com `models.py`, `services.py` e `routes.py`:

- **auth**: cadastro, login e papéis (paciente ou operador).
- **pacientes**: perfil e convênio do paciente.
- **triagem**: catálogo de sintomas, registro da triagem e regras de prioridade.
- **unidades**: unidades de saúde, convênios aceitos, lotação e recomendação por distância.
- **encaminhamentos**: “Estou indo”, protocolo e fila da unidade.

### 8.3 Modelo de dados inicial

| Entidade | Principais atributos | Relacionamentos |
|---|---|---|
| Usuario | id, email, senha_hash, papel (paciente/operador), criado_em | 1:1 com Paciente ou N:1 com Unidade (operador) |
| Paciente | nome, cpf, data_nascimento, telefone, contato_emergencia, consentimento_em | N:1 com Convenio; 1:N com Triagem |
| Convenio | nome (inclui “Particular”) | N:N com Unidade |
| Unidade | nome, tipo (PA/clínica/hospital), endereço, latitude, longitude, horário, telefone | N:N com Convenio; 1:N com RegistroLotacao e Encaminhamento |
| Sintoma | nome, descricao, sinal_alarme (bool) | N:N com Triagem |
| Triagem | queixa_principal, intensidade, inicio_sintomas, temperatura, prioridade, criada_em | N:1 com Paciente; N:N com Sintoma; 1:1 com Encaminhamento |
| Encaminhamento | protocolo, status, criado_em, atualizado_em | N:1 com Triagem e com Unidade |
| RegistroLotacao | nivel (baixa/média/alta), registrado_em | N:1 com Unidade e com Usuario (operador) |

### 8.4 Principais endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| POST | /api/auth/cadastro | Cadastra um paciente |
| POST | /api/auth/login | Autentica e retorna o token |
| GET | /api/sintomas | Lista o catálogo de sintomas |
| POST | /api/triagens | Registra a triagem e retorna a prioridade sugerida |
| GET | /api/unidades?convenio=&lat=&lng= | Lista unidades compatíveis, ordenadas por lotação e distância |
| POST | /api/encaminhamentos | “Estou indo”: cria o encaminhamento e o protocolo |
| GET | /api/encaminhamentos/fila | Fila da unidade do operador logado |
| PATCH | /api/encaminhamentos/{id} | Atualiza o status do encaminhamento |
| POST | /api/unidades/{id}/lotacao | Registra a lotação atual da unidade |
| GET | /api/health | Verificação de funcionamento da API |

## 9. Etapas de desenvolvimento (2º bimestre)

| Etapa | Entregas |
|---|---|
| 1. Configuração | Repositório, venv, pyproject.toml, Application Factory, extensões, projeto Vue com Vite e seed de unidades e convênios |
| 2. Autenticação | Modelos de usuário e paciente, cadastro, login com token, telas de login e cadastro |
| 3. Triagem | Catálogo de sintomas, formulário em etapas, regras de prioridade com testes automatizados |
| 4. Unidades | Endpoint de recomendação (convênio, lotação e distância) e tela de unidades recomendadas |
| 5. Encaminhamento e operador | “Estou indo”, protocolo, fila da unidade, atualização de status e de lotação |
| 6. Finalização | Testes, ajustes de interface, itens Should se houver tempo, documentação e apresentação |

## 10. Riscos e limitações

- **Regras de triagem simplificadas:** servem para demonstração e precisam ser validadas por profissionais de saúde antes de qualquer uso real.
- **Lotação depende do operador:** se a unidade não atualizar o nível, a informação fica desatualizada. Por isso o horário da última atualização é sempre exibido.
- **Dados de demonstração:** unidades, convênios e operadores do MVP são fictícios, carregados por seed.
- **Localização:** se o paciente negar a geolocalização, a lista é ordenada só por lotação.