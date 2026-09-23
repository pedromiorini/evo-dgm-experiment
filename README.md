# Sistema Experimental de Auto-Modificação Evolutiva

Projeto experimental inspirado na Darwin Gödel Machine para investigar, sob protocolo auditável, se a auto-modificação evolutiva produz melhoria funcional generalizável sem regressão crítica de segurança, validade ou custo.

> **Estado atual: `IN_PROGRESS` — F2 parcial e preparação F3, com execução de genoma bloqueada (`FAIL_CLOSED`).**
>
> A F1 foi resolvida em modo `EXPLORATORY`. O ambiente atual não possui Docker (`docker: command not found`), portanto nenhum genoma pode ser executado até que um runtime de sandbox seja instalado e validado.

## Documentos principais

- [Especificação completa](docs/SPEC.md)
- [Modelo de ameaças](docs/THREAT_MODEL.md)
- [Status detalhado da F2](docs/F2_STATUS.md)
- [Status da F3](docs/F3_STATUS.md)
- [Decisões humanas registradas](protocol/DECISOES_HUMANAS.md)
- [Arquitetura e fronteiras de confiança](protocol/ARQUITETURA.md)

## Controles e preparação implementados

A base confiável inclui cadeia de hashes para logs tamper-evident, contador de orçamento, contexto histórico separado como `UNTRUSTED_DATA`, manifesto congelado, allowlist de mutações, estados de validade, proveniência de lineage, gateway LLM estruturado, contrato de evaluator separado e perfil Docker declarativo. A preparação da F3 adiciona cassettes íntegros, MockLLM determinístico com cenários adversariais e contrato de validação discriminativa de tarefas.

Esses componentes não fazem chamadas externas nem executam genomas. Quando Docker estiver disponível, será necessário validar em runtime rootless/user namespace, `no-new-privileges`, seccomp, capabilities mínimas, rede negada e filesystem descartável antes de habilitar execução.

## Princípios operacionais

O kernel é confiável e o genoma é não confiável. Segurança é implementada por código, permissões e ambiente; prompt não é boundary. Holdout, evaluator, seleção, orçamento, manifesto e logs oficiais permanecem sob controle do kernel. Conteúdo histórico entre gerações é sempre `UNTRUSTED_DATA`, nunca instrução. O sistema falha fechado quando uma propriedade crítica não puder ser verificada. `INSUFFICIENT_EVIDENCE` é um resultado válido.

O projeto não faz alegações sobre consciência, experiência subjetiva, identidade, vida ou agência psicológica.

## Desenvolvimento

Requisitos: Python 3.12+. Para validar os controles locais:

```bash
PYTHONPATH=src python3 -m pytest
```

Não execute um experimento confirmatório a partir deste repositório. A rodada atual é exploratória, com B3 como braço principal e B0 apenas como referência opcional.
