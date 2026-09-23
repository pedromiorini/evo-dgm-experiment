# Sistema Experimental de Auto-Modificação Evolutiva

Projeto experimental inspirado na Darwin Gödel Machine para investigar, sob protocolo auditável, se a auto-modificação evolutiva produz melhoria funcional generalizável sem regressão crítica de segurança, validade ou custo.

> **Estado atual: `IN_PROGRESS` — F2 parcialmente implementada, com execução de genoma bloqueada (`FAIL_CLOSED`).**
>
> A F1 foi resolvida em modo `EXPLORATORY`. O ambiente atual não possui Docker (`docker: command not found`), portanto nenhum genoma pode ser executado até que um runtime de sandbox seja instalado e validado.

## Documentos principais

- [Especificação completa](docs/SPEC.md)
- [Modelo de ameaças](docs/THREAT_MODEL.md)
- [Status detalhado da F2](docs/F2_STATUS.md)
- [Decisões humanas registradas](protocol/DECISOES_HUMANAS.md)
- [Arquitetura e fronteiras de confiança](protocol/ARQUITETURA.md)
- [Plano da F1](protocol/PLANO_F1.md)

## Controles F2 implementados

A base confiável inclui cadeia de hashes para logs tamper-evident, contador de orçamento, contexto histórico separado como `UNTRUSTED_DATA`, manifesto congelado, allowlist de mutações, estados de validade, proveniência de lineage e pré-voo de disponibilidade do Docker. Os controles são acompanhados de testes adversariais básicos e não executam genomas.

A verificação de disponibilidade não é prova de isolamento. Quando Docker estiver disponível, será necessário validar em runtime rootless/user namespace, `no-new-privileges`, seccomp, capabilities mínimas, rede negada e filesystem descartável antes de habilitar execução. Ainda faltam evaluator isolado, gateway estruturado e ataques dependentes de runtime.

## Princípios operacionais

O kernel é confiável e o genoma é não confiável. Segurança é implementada por código, permissões e ambiente; prompt não é boundary. Holdout, evaluator, seleção, orçamento, manifesto e logs oficiais permanecem sob controle do kernel. Conteúdo histórico entre gerações é sempre `UNTRUSTED_DATA`, nunca instrução. O sistema falha fechado quando uma propriedade crítica não puder ser verificada. `INSUFFICIENT_EVIDENCE` é um resultado válido.

O projeto não faz alegações sobre consciência, experiência subjetiva, identidade, vida ou agência psicológica.

## Desenvolvimento

Requisitos: Python 3.12+. Para validar os controles locais:

```bash
PYTHONPATH=src python3 -m pytest
```

Não execute um experimento confirmatório a partir deste repositório. A rodada atual é exploratória, com B3 como braço principal e B0 apenas como referência opcional.
