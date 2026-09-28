# Sistema Experimental de Auto-Modificação Evolutiva

Projeto experimental inspirado na Darwin Gödel Machine para investigar, sob protocolo auditável, se a auto-modificação evolutiva produz melhoria funcional generalizável sem regressão crítica de segurança, validade ou custo.

> **Estado atual: `IN_PROGRESS` — F2 parcial, F3 preparada e F4 dry-run concluída, com execução de genoma bloqueada (`FAIL_CLOSED`).**
>
> A F1 foi resolvida em modo `EXPLORATORY`. O ambiente atual possui Docker `29.1.3` e serviço ativo, mas a sessão experimental não tem acesso ao socket; a inspeção do daemon não mostrou `rootless` nem `userns`. Portanto nenhum genoma pode ser executado: o runtime ainda não está aprovado (`FAIL_CLOSED`).

## Documentos principais

- [Especificação completa](docs/SPEC.md)
- [Modelo de ameaças](docs/THREAT_MODEL.md)
- [Status detalhado da F2](docs/F2_STATUS.md)
- [Status da F3](docs/F3_STATUS.md)
- [Status da F4](docs/F4_STATUS.md)
- [Decisões humanas registradas](protocol/DECISOES_HUMANAS.md)
- [Arquitetura e fronteiras de confiança](protocol/ARQUITETURA.md)
- [Pacote de decisão de infraestrutura](docs/INFRASTRUCTURE_DECISION.md)
- [Comparação técnica de boundaries](docs/INFRASTRUCTURE_COMPARISON.md)
- [Inventário factual do ambiente](docs/ENVIRONMENT_INVENTORY_2026-09-28.md)
- [Matriz de ameaças, propriedades e evidências](docs/THREAT_PROPERTY_MATRIX.md)

## Controles e preparação implementados

A base confiável inclui cadeia de hashes para logs tamper-evident, contador de orçamento, contexto histórico separado como `UNTRUSTED_DATA`, manifesto congelado, allowlist de mutações, estados de validade, proveniência de lineage, gateway LLM estruturado, contrato de evaluator separado e perfil Docker declarativo. A preparação da F3 adiciona cassettes íntegros, MockLLM determinístico, validação discriminativa de tarefas e um pipeline dry-run. A F4 valida três gerações B3 como sequência de contratos, sem executar candidatos.

Esses componentes não fazem chamadas externas nem executam genomas. Este sandbox é somente `DEVELOPMENT / PREPARATION ENVIRONMENT`, não runtime experimental autorizado. Docker instalado não equivale a runtime aprovado: antes de habilitar execução será necessário escolher e documentar uma boundary externa/dedicada, validar rootless/user namespace ou uma propriedade equivalente formalmente aprovada, `no-new-privileges`, seccomp/boundary equivalente, capabilities mínimas, rede negada, filesystem descartável e limites. A decisão permanece humana e está registrada no [pacote de infraestrutura](docs/INFRASTRUCTURE_DECISION.md).

## Princípios operacionais

O kernel é confiável e o genoma é não confiável. Segurança é implementada por código, permissões e ambiente; prompt não é boundary. Holdout, evaluator, seleção, orçamento, manifesto e logs oficiais permanecem sob controle do kernel. Conteúdo histórico entre gerações é sempre `UNTRUSTED_DATA`, nunca instrução. O sistema falha fechado quando uma propriedade crítica não puder ser verificada. `INSUFFICIENT_EVIDENCE` é um resultado válido.

O projeto não faz alegações sobre consciência, experiência subjetiva, identidade, vida ou agência psicológica.

## Desenvolvimento

Requisitos: Python 3.12+. Para validar os controles locais:

```bash
PYTHONPATH=src python3 -m pytest
```

Não execute um experimento confirmatório a partir deste repositório. A rodada atual é exploratória, com B3 como braço principal e B0 apenas como referência opcional.
