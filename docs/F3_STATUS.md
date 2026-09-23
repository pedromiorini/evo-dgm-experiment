# Status da F3 — Genome0, MockLLM e tarefas

## Estado

A preparação inicial da F3 foi implementada localmente e publicada, sem rede, sem provedor LLM real e sem execução de genoma. O estado experimental continua `EXPLORATORY`; os componentes abaixo são contratos de teste e replay.

## Componentes

| Componente | Estado | Limitação atual |
|---|---|---|
| Cassette íntegro | Implementado | Replay exige request exatamente igual e não substitui nova execução sem evidência |
| MockLLM | Implementado | Cenários determinísticos, não representa desempenho de LLM real |
| Cenários adversariais | Implementado | Inclui mutação inválida, regressão, injection histórica, resposta malformada e falsa aprovação |
| Validação de tarefas | Implementado | Contrato exige referência, nulo, adversarial, metamórfico e hardcoding |
| Genome0/loop | Não implementado | Depende da conclusão dos controles de sandbox/evaluator |

## Critério de interpretação

Passar nos testes desta etapa valida apenas os contratos e o pipeline local. Não valida a hipótese científica, generalização, segurança absoluta ou desempenho de um modelo real. Dados de MockLLM não podem ser usados como evidência confirmatória.

## Próximos bloqueios

Antes do F4, ainda é necessário um ambiente Docker validado, um executor de sandbox que aplique o perfil restritivo, evaluator real separado e testes de ataques de runtime. Depois disso, o pipeline poderá ser exercitado com pelo menos três gerações no MockLLM, ainda como validação de engenharia.
