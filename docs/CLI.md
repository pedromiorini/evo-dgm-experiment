
`preflight` executa somente o probe real do Docker e reporta a evidência parcial, sem executar código de candidato. Mesmo quando algumas propriedades passam, o comando mantém `genome_execution=BLOCKED` e `status=FAIL_CLOSED` se qualquer requisito falhar.
