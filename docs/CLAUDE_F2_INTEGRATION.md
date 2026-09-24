# Integração seletiva dos controles Claude F2

## Escopo integrado

Foram incorporados apenas componentes que não executam subprocessos nem habilitam genomas: `KernelLog` persistente em JSONL, verificação de cadeia após reabertura, status explícito `TAMPER_EVIDENT_LOCAL_ONLY`, workdir descartável com validação de caminhos e ambiente mínimo com allowlist.

## Escopo não integrado

O `SubprocessSandbox` do pacote alternativo não foi copiado. Embora seus testes de CPU, memória, processos, timeout e rede tenham passado no diretório temporário do ZIP, ele é explicitamente `subprocess_dev_only` e não fornece isolamento de filesystem. A base atual continua sem executor de produção e sem downgrade silencioso de Docker/VM para subprocesso.

Também não foram copiados automaticamente a árvore `kernel/`, a CLI alternativa, o ledger alternativo, o evaluator alternativo ou a matriz de ataques, porque eles usam APIs e layout diferentes da arquitetura `src/evo_kernel/`. A integração desses componentes exigiria adaptação individual e nova revisão.

## Testes

A suíte do projeto atual passou em **36 testes**. Os novos casos verificam recuperação do log após restart, adulteração do payload, rejeição de caminhos absolutos e `..`, escrita apenas de arquivos declarados e rejeição de variáveis de ambiente não permitidas.

## Classificação

O log local continua sendo `TAMPER_EVIDENT_LOCAL_ONLY`. A cadeia detecta alterações e inconsistências após recuperação, mas não prova que o arquivo original não foi substituído por uma cadeia alternativa consistente. Para uso confirmatório ainda são necessárias persistência protegida e âncora externa independente.
