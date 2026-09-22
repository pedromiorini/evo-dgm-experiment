# Decisões humanas — F1

**Estado:** `PENDING_APPROVAL`

Este documento atende à primeira saída obrigatória da F1. As recomendações abaixo são técnicas e não constituem aprovação. Nenhum item deve ser tratado como congelado até que uma pessoa responsável registre a decisão, a justificativa e a data em uma revisão versionada.

## Recomendação inicial

Começar em modo **EXPLORATORY**, com tarefas de programação verificadas automaticamente por I/O, templates versionados, testes discriminativos e MockLLM. O modo CONFIRMATORY deve ser considerado somente depois de um novo congelamento de protocolo, SAP completo e aprovação humana.

## Matriz de decisão

| ID | Decisão requerida | Recomendação inicial | Consequência se adotada | Status |
|---|---|---|---|---|
| D01 | SESOI | Definir após piloto separado; não usar valor pós-hoc no confirmatório | Determina o menor efeito relevante | Pendente |
| D02 | Alfa | Pré-especificar antes de dados confirmatórios, por exemplo 0,05 | Controla o critério de inferência | Pendente |
| D03 | Poder/amostra | Planejar em nível de `run/seed` para alegação PROCESS; não contar instâncias como runs | Define número máximo de runs e limitações | Pendente |
| D04 | Teto de custo por tarefa | Usar `CUSTO_POR_TAREFA_IGUAL` como estimando primário | Compara braços sob mesmo custo operacional por tarefa | Pendente |
| D05 | Orçamento total | Fixar no manifesto por braço/run, sem ajuste ao campeão | Permite auditoria e evita matching pós-hoc | Pendente |
| D06 | Máximo de runs | Definir antes do piloto confirmatório | Limita seleção adaptativa e custo | Pendente |
| D07 | Alegação primária | Começar com `ARTIFACT`; migrar para `PROCESS` apenas com runs independentes suficientes | Preserva dependência família → instância | Pendente |
| D08 | Isolamento | Preferir VM/gVisor/Firecracker/Kata; caso indisponível, `FAIL_CLOSED` | Define se qualquer execução pode começar | Pendente |
| D09 | Estimando de custo | Escolher exatamente um: `CUSTO_POR_TAREFA_IGUAL` ou `CUSTO_TOTAL_IGUAL` | Mudar após congelamento cria novo experimento | Pendente |
| D10 | Regra de finalistas B2/B3 | Congelar regra antes dos dados; usar a mesma regra em B2 e B3 | Evita seleção pós-hoc | Pendente |
| D11 | Política da FINAL | Recomenda-se `FIXED_FINAL_SET` para a primeira versão | Inferência condicional ao conjunto selado | Pendente |
| D12 | Domínio das tarefas | Programação com I/O, templates e testes ocultos discriminativos | Permite validação automática e testes metamórficos | Pendente |
| D13 | Modo | `EXPLORATORY` para F3–F5; `CONFIRMATORY` somente após novo congelamento | Impede alegações confirmatórias indevidas | Pendente |
| D14 | Versão/modelo do LLM | Fixar provedor, modelo, versão e parâmetros no manifesto | Controla confundimento do LLM | Pendente |
| D15 | Política de dependências | Permitir apenas stdlib, pytest, pyyaml, httpx e Docker SDK inicialmente | Dependência adicional exige aprovação explícita | Pendente |
| D16 | Licença do repositório | Escolher antes da publicação pública | Define reutilização do código e documentos | Pendente |

## Critério de encerramento da F1

A F1 somente pode ser marcada como concluída quando houver decisões explícitas para D01–D16, arquitetura e fluxo de informação documentados, threat model versionado, plano de piloto, critérios de aceitação e registro da aprovação humana. Até então, o estado global permanece `NOT_STARTED`.

## Registro de aprovação

- **Responsável:** não definido
- **Data:** não definida
- **Revisão/commit:** não definido
- **Decisão:** não aprovada
