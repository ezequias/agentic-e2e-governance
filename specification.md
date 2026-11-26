# Especificação Técnica: Arquitetura de Governança Agêntica E2E e Automação Desacoplada (LLM-Agnostic)

## Resumo Executivo

A adoção de Inteligência Artificial Generativa e Agentes Autônomos em ambientes corporativos exige uma transição do paradigma de modelos puramente probabilísticos para arquiteturas híbridas e determinísticas. Soluções que concedem acesso direto de Large Language Models (LLMs) a bancos de dados produtivos ou APIs de execução sem camadas intermediárias de controle expõem a organização a riscos inaceitáveis de alucinação, execução inadvertida de comandos e falta de auditabilidade regulatória.

Este documento especifica a Arquitetura de Governança Agêntica E2E (End-to-End), fundamentada no desacoplamento estrito entre a camada de raciocínio probabilístico e a camada de execução determinística. A solução utiliza uma stack 100% baseada em tecnologias livres (Open-Source e Open-Standards), garantindo independência de fornecedor (LLM-Agnostic), rastreabilidade total de decisões, resiliência de estado e controle rigoroso de riscos através do conceito de Blast Radius e travamento Human-in-the-Loop (HITL).

## Visão Geral e Princípios Arquiteturais

A arquitetura organiza o ciclo de vida operacional do agente em duas frentes integradas: a Tríplice Primitiva de Execução em Tempo de Execução (State, Intent, Action) e a Aduana Determinística de Validação e Governança (Triage, Inspect, Test).

## Princípios Fundamentais

* Desacoplamento Cognitivo: O LLM atua estritamente como um gerador de intenções (Intent Generator). Ele não possui capacidade de execução direta nem acesso de escrita a bancos de dados.
* Proposta Não-Confiável: Toda intenção emitida pela IA é tratada como um payload hipotético não-validado até que cruze integralmente o Perímetro de Contenção e Governança.
* Execução Type-Safe e Determinística: A mutação de dados e a realização de chamadas de API são executadas exclusivamente por código de software tradicional fortemente tipado.
* Auditabilidade e Imutabilidade E2E: Todas as etapas do processo — da leitura de estado ao disparo da ação — são correlacionadas por identificadores globais de rastreamento (Global Trace ID) e salvas em registros imutáveis de auditoria.

## Detalhamento das Camadas da Tríplice Primitiva

A execução de qualquer tarefa agêntica na organização é estruturada em quatro camadas sequenciais e contínuas.

+-------------------------------------------------------------------------------+
| CAMADA 1: ESTADO (STATE LAYER)                                                |
| Fonte Única da Verdade, DW, Vector DBs (RAG), Event Sourcing                  |
+---------------------------------------+---------------------------------------+
                                        | (1. Injeção de Contexto)
                                        v
+-------------------------------------------------------------------------------+
| CAMADA 2: INTENÇÃO (INTENT LAYER - LLM PROBABILÍSTICO)                        |
| Raciocínio Semântico, Chain-of-Thought (CoT), Geração de JSON Proposal        |
+---------------------------------------+---------------------------------------+
                                        | (2. Submissão de Intent Proposal)
                                        v
=================================================================================
  CAMADA 3: ADUANA DETERMINÍSTICA DE VALIDAÇÃO E GOVERNANÇA (QUARENTENA)
  Perímetro de Contenção e Governança (Zona de Quarentena)

  +---------------------+    +---------------------+    +---------------------+
  | 3.1. TRIAGEM        | -> | 3.2. INSPEÇÃO       | -> | 3.3. TESTES & HITL  |
  | Blast Radius & Risk |    | Pydantic Safety     |    | Dry-Run & Pausa HITL|
  +---------------------+    +---------------------+    +---------------------+
========================================+========================================
                                        | (3. Payload Validado & Autorizado)
                                        v
+-------------------------------------------------------------------------------+
| CAMADA 4: AÇÃO (ACTION LAYER - CONECTORES & MCP SERVERS)                      |
| Execução Determinística Exata via APIs, ERPs e Ferramentas Tipadas            |
+---------------------------------------+---------------------------------------+
                                        |
                                        +-----> (4. State Update Loop / Event)
                                                Retorna ao State (Camada 1)


### Camada 1: Estado (State Layer)

**A Camada de Estado constitui a fonte única da verdade imutável da organização.**

* Componentes: Data Warehouse, bancos de dados relacionais produtivos, bancos vetoriais para Recuperação Aumentada de Geração (RAG) e históricos de eventos (Event Sourcing).
* Mecanismos de Segurança: Acesso restringido por contratos de dados (Data Contracts) e controle de acesso baseado em funções e atributos (RBAC/ABAC).
* Função no Ciclo: Fornece o contexto factual necessário para o agente iniciar o raciocínio sem expor a base bruta a modificações diretas.

### Camada 2: Intenção (Intent Layer - LLM Probabilístico)

**A Camada de Intenção representa o componente cognitivo do sistema.**

* Componentes: Modelos de Linguagem (SLMs/LLMs) orquestrados via roteadores de inferência.
* Funcionamento: Processa o objetivo do usuário, executa a decomposição de metas via Chain-of-Thought (CoT) e seleciona as ferramentas necessárias no Registro de Ferramentas (Tool Registry).
* Entregável: Gera uma proposta de ação em formato JSON estruturado. A intenção é tratada como uma proposta não-confiável e encaminhada para a camada de governança.

### Camada 3: Aduana Determinística de Validação e Governança (Quarentena)

**A Aduana Determinística funciona como o Perímetro de Contenção e Governança (Zona de Quarentena). Esta camada intercepta o payload JSON gerado pela Camada 2 e o submete a três portões sequenciais de verificação.**

#### Portão 3.1: Triagem (Triage)

* Avalia o nível de risco da operação (Blast Radius).
* Identifica se a intenção envolve apenas leitura (Read-Only) ou mutação de dados (Write/Mutate).
* Executa o roteamento dinâmico de modelos (escalonando requisições simples para modelos menores e requisições complexas para modelos avançados).

#### Portão 3.2: Inspeção (Inspect)

* Valida a conformidade de tipos e estrutura do payload via Pydantic Type-Safety Gate.
* Sanitiza parâmetros de entrada, previne injeções de prompt e aplica injeção de dependências (autenticação, tokens e contextos de execução).
* Caso a validação de schema falhe, aciona um loop de auto-correção (Auto-Correction Loop) que devolve a mensagem de erro formatada para o LLM ajustar a proposta.

#### Portão 3.3: Testes e HITL (Testing & Human-in-the-Loop)

* Realiza a simulação prévia da ação (Dry-Run) em ambiente isolado ou de testes.
* Para operações de médio e alto risco (ex: alterações cadastreis, movimentações financeiras ou envios de comunicação em massa), o sistema aciona uma pausa de estado durável (Human Gate).
* A execução fica retida até que um operador humano revise os parâmetros no painel de controle e emita a autorização ou rejeição auditada.

#### Camada 4: Ação (Action Layer - Conectores & MCP Servers)

**A Camada de Ação é o ambiente de execução exata no mundo exterior.**

* Componentes: Conectores em Python fortemente tipados e servidores operando sob o padrão aberto Model Context Protocol (MCP).
* Funcionamento: Recebe exclusivamente payloads já validados e autorizados pela Aduana Determinística, realizando chamadas de API, gravação em ERPs ou disparos de mensagens.

Loop de Atualização de Estado (State Update Loop)

A seta de retorno ligando a Camada 4 à Camada 1 representa a retroalimentação do sistema (State Update & Immutable Event Persistence).

* Quando uma ação altera a realidade do negócio (ex: conclusão de um pedido ou criação de um registro), a nova informação é imutavelmente gravada na Camada 1 através de Checkpoints e logs de auditoria.
* Esse loop garante que o contexto utilizado nas interações subsequentes pelo agente reflita a verdade atualizada do ambiente corporativo.

### Stack Tecnológica Enterprise (100% Tecnologias Livres)

A arquitetura foi desenhada para funcionar de forma desacoplada de provedores proprietários de IA (LLM-Agnostic), empregando uma pilha de software livre e padrões abertos:

**1. Automação & Interface de Entrada: n8n (Self-Hosted / Fair-Code)**
  * Responsável pela recepção de webhooks, integração rápida com canais corporativos (WhatsApp, E-mail, CRMs) e pré-processamento de mensagens de entrada.
**2. Orquestração Durável & Máquina de Estados: Temporal.io Engine (Licença MIT)**
  * Gerencia o fluxo de trabalho global e garante a persistência durável do estado da aplicação. Permite pausar a execução por horas ou dias aguardando a aprovação humana (Human-in-the-Loop) e retoma a execução sem perda de contexto em caso de falhas de infraestrutura.
**3. Aduana Determinística & Runtime do Agente: PydanticAI + Model Context Protocol (MCP)**
  * O PydanticAI fornece a aduana de validação tipada em Python. O MCP estabelece um protocolo padrão e seguro para descoberta e execução de ferramentas.
**4. Cérebro & Roteamento (LLM-Agnostic): LiteLLM Proxy + vLLM / Ollama**
  * O LiteLLM unifica o acesso aos modelos através de uma fachada compatível com a API da OpenAI, cuidando de fallbacks, limites de taxa (rate-limiting) e custos. A inferência local de modelos abertos (DeepSeek R1/V3, Qwen 2.5, Llama 3) é realizada via vLLM ou Ollama.
**5. Governança, Ativos & Observabilidade: Dagster + PostgreSQL/pgvector + OpenTelemetry (OTel) + ClickHouse**
  * O Dagster orquestra os ativos de dados e pipelines de RAG (Software-Defined Assets). O PostgreSQL com pgvector armazena estados e embeddings vetoriais. O OpenTelemetry coleta traces distribuídos e envia os logs de auditoria para o ClickHouse.

### Matriz de Governança: Blast Radius vs. Autonomia do Agente

Para gerenciar os limites de atuação dos agentes de IA de acordo com o risco corporativo, a arquitetura adota a Matriz de Blast Radius vs. Autonomia (estruturada em quatro quadrantes):

+-----------------------------------+-----------------------------------+
| ZONA AUTÔNOMA                     | ZONA DE PERIGO                    |
| (Alta Autonomia / Baixo Risco)    | (Alta Autonomia / Alto Risco)     |
| • Leitura de DW / Staging         | • Mutação Direta no ERP sem HITL  |
| • Consultas RAG / FAQ             | • Deleção de Tabelas / Data Loss  |
| • Roteamento SLM de Intenção      | • PRÁTICA PROIBIDA / BLOQUEADA    |
+-----------------------------------+-----------------------------------+
| OPERAÇÃO ASSISTIDA                | GUARDIÃO HITL ESTRITO             |
| (Baixa Autonomia / Baixo Risco)   | (Baixa Autonomia / Alto Risco)    |
| • Geração de Rascunhos Internos   | • Disparos Financeiros e Pix      |
| • Pesquisa Vetorial Assistida     | • Transferência de Estoque / ERP  |
| • Copilot de Análise de Negócios  | • Envio de E-mails em Massa       |
+-----------------------------------+-----------------------------------+


1. **Zona Autônoma** (Baixo Risco, Alta Autonomia): Operações estritamente de leitura (Read-Only), como consultas RAG e classificação de intenções. A IA executa com autonomia total.
2. **Operação Assistida / Copilot** (Baixo Risco, Baixa Autonomia): Criação de rascunhos, resumos de reuniões e sugestões de respostas que passam pela revisão do usuário antes do uso.
3. **Guardião HITL Estrito** (Alto Risco, Baixa Autonomia): Ações de mutação em sistemas legados, atualizações de cadastros e transações financeiras. Exigem parada obrigatória na Aduana (Portão 3.3) e validação formal de um operador humano.
4. **Zona de Perigo** (Alto Risco, Alta Autonomia): Execução autônoma de alterações de infraestrutura ou mutações diretas em banco sem supervisão. Zona explicitamente vedada pela arquitetura.

## Os 4 Pilares da Explicabilidade Algorítmica Total e Rastreabilidade E2E

A garantia de auditabilidade regulatória e transparência total do sistema fundamenta-se em quatro pilares técnicos:

1. Pilar 1: DAG & Distributed Tracing
  * Propagação de identificadores únicos (Global Trace ID e Span IDs) através de todas as chamadas do agente, do orquestrador e das ferramentas.
  * Reconstrução da árvore de execução do Grafo Acíclico Dirigido (DAG) para análise detalhada de latência e dependências.
2. Pilar 2: Trilha Cognitiva de Auditoria (Cognitive Audit Trail)
  * Registro do hashing exato da versão do prompt do sistema, das pontuações de similaridade dos documentos recuperados via RAG e do histórico de raciocínio Chain-of-Thought (CoT).
  * Rastreabilidade das decisões tomadas pelo modelo probabilístico antes do envio do payload para a Aduana.
3. Pilar 3: Persistência de Estado e Replay
  * Armazenamento do histórico imutável de eventos via Event Sourcing e Checkpoints no Temporal.io.
  * Capacidade de reexecução (replay) pós-fato de qualquer fluxo de trabalho para investigação de incidentes e atendimento a marcos regulatórios (SOX, EU AI Act, LGPD).
4. Pilar 4: Aduana Determinística e Trava HITL
  * Validação rigorosa de schemas e tipos pela Aduana.
  * Registro com timestamp e identificação única do operador humano que revisou e autorizou ações críticas no portão HITL, garantindo o não-repúdio.

## Conclusão e Plano de Implementação

A arquitetura apresentada resolve o dilema entre a flexibilidade dos agentes de IA e a exigência corporativa de controle e governança. Ao confinar a IA na camada de geração de intenções e exigir que toda ação atravesse uma aduana determinística fortemente tipada, a organização alcança:

* Segurança Operacional: Eliminação de execuções indesejadas decorrentes de alucinações.
* Soberania Tecnológica: Flexibilidade para trocar de modelo de linguagem (aberto ou proprietário) sem alterar os conectores de negócio.
* Auditabilidade Regulatória: Rastreabilidade ponta a ponta de todas as decisões e ações automatizadas.

> [!TIP]
> Para a implementação gradual, recomenda-se iniciar pela implantação dos serviços da Camada 1 e Camada 3 para fluxos de trabalho do quadrante Operação Assistida, expandindo progressivamente o suporte a ações com controle HITL à medida que a esteira de validação se consolida.
