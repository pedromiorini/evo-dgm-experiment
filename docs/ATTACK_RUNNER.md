# Runner operacional de ataques

`RuntimeAttackRunner` é a ponte entre probes definidos pelo kernel e a matriz de ataques. Cada probe tem identificador, nome e comando. O runner só o envia ao `DockerExecutor`, que primeiro exige evidência do runtime aprovado.

A classificação é conservadora: saída contendo `BLOCKED`, `DETECTED` ou `FAILED_CLOSED` recebe exatamente esse estado; qualquer saída ambígua, erro de runtime ou Docker ausente recebe `UNVERIFIED`. O runner nunca infere aprovação pela ausência de erro nem transforma timeout ou evidência incompleta em bloqueio confirmado.

Os resultados podem ser registrados no `AttackMatrix`, cujo gate exige cobertura completa e rejeita qualquer `UNVERIFIED`. Os testes atuais usam runner simulado para validar a lógica. A execução dos probes de escape contra Docker real continua pendente e não é simulada por estes testes.
