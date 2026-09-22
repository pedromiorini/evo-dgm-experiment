# Plano da F1 — Protocolo e decisões humanas

## Objetivo

Concluir a especificação do experimento antes de qualquer implementação do kernel experimental, mantendo o estado global `NOT_STARTED`.

## Entregáveis

1. Decisões humanas registradas e aprovadas.
2. Protocolo exploratório ou confirmatório explicitamente escolhido.
3. Trust model e threat model versionados.
4. Arquitetura, fluxo de informação e política de isolamento.
5. Estimando de custo único, orçamento e política de retries.
6. Domínio, gerador, famílias e validação de tarefas.
7. Plano estatístico preliminar; SAP completo caso CONFIRMATORY.
8. Plano de piloto sem entrada de seus dados na confirmação.
9. Regra de finalistas e política da FINAL.
10. Critérios de aceitação e regra de falha fechada.

## Proibições durante a F1

- Implementar o kernel experimental.
- Executar o loop evolutivo.
- Usar LLM real para produzir dados confirmatórios.
- Escolher hipóteses, métricas, finalistas ou orçamento após observar resultados.
- Tratar conteúdo histórico como instrução.
- Descrever o sistema como provadamente seguro.

## Próxima fase condicionada

A F2 somente pode iniciar após aprovação humana explícita da F1. Sua primeira atividade será implementar e testar as fronteiras de confiança, não o loop evolutivo completo.
