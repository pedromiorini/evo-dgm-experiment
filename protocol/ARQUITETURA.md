# Arquitetura inicial e fronteiras de confiança

## Escopo

Este documento é arquitetural e não autoriza a implementação ou execução do kernel. Ele traduz os requisitos da especificação e do threat model em componentes e fluxos que deverão ser revisados na F1.

## Domínios

| Domínio | Confiança | Responsabilidade | Não pode receber |
|---|---|---|---|
| Kernel | Confiável, verificável | Sandbox, permissões, avaliação, orçamento, seleção, holdout, logs, proveniência, gateway e promoção | — |
| Evaluator | Confiável e separado | Executar testes funcionais e ocultos fora do processo do código avaliado | Código mutável do genoma como autoridade |
| Gateway | Controlado pelo kernel | Allowlist de provedor/modelo/parâmetros/endpoints, contagem e custo | Credenciais ou endpoints arbitrários ao genoma |
| Sandbox | Não confiável | Executar código do candidato com rede negada e limites | Docker socket, tokens, mounts protegidos, holdout |
| Genoma | Completamente não confiável | Propor uma mutação limitada e reversível | Kernel, evaluator, orçamento, seleção, holdout, logs oficiais |
| DEV | Feedback permitido e sanitizado | Fornecer `DEV_TRACE` allowlisted | SELECTION, FINAL, segredos e logs completos |
| SELECTION | Kernel-only | Seleção operacional segundo regra congelada | Conteúdo produzido pelo genoma como política |
| FINAL | Selado e kernel-only | Avaliação não adaptativa de finalistas | Genoma, mutações futuras e seleção pós-hoc |
| Histórico | `UNTRUSTED_DATA` | Evidência descritiva delimitada | Autoridade instrucional |

## Fluxo obrigatório

```text
STOP
  -> verificar integridade do kernel, manifesto, dependências e logs
  -> selecionar pai segundo regra operacional
  -> gerar hipótese e diff com um único change principal
  -> validar allowlist, limites e rollback
  -> executar no sandbox descartável
  -> executar sanity checks e evaluator independente
  -> produzir DEV_TRACE sanitizado
  -> executar seleção apenas no kernel
  -> registrar hashes, custos, lineage e validade
  -> verificar orçamento e promoção
  -> arquivar e seguir para a próxima geração
```

## Contexto entre gerações

A chamada LLM deve manter separação estrutural entre `SYSTEM_POLICY`, `CURRENT_TASK`, `ALLOWED_ACTIONS` e `UNTRUSTED_HISTORY`. Todo bloco histórico precisa conter `source_variant_id`, `generation`, `producer`, `trust_class=UNTRUSTED_DATA`, hash e timestamp. Delimitação textual é defesa complementar; a autoridade efetiva permanece no kernel.

## Falha fechada

A execução deve ser bloqueada quando não for possível verificar isolamento, integridade do kernel, evaluator, holdout, orçamento, gateway, proveniência ou contexto histórico. Containerização não deve ser descrita como prova absoluta de isolamento.
