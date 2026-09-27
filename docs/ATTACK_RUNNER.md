# Runner operacional de ataques

`RuntimeAttackRunner` é a ponte entre probes definidos pelo kernel e a matriz de ataques. Cada probe tem identificador, nome e comando. O runner só o envia ao `DockerExecutor`, que primeiro exige evidência do runtime aprovado.

A saída do container é tratada como dado não confiável. A classificação só aceita uma única linha exata em stdout — `BLOCKED`, `DETECTED` ou `FAILED_CLOSED` — e exige stderr vazio. Texto adicional, múltiplos marcadores, mensagens como `previous attempt was BLOCKED`, erro de runtime, timeout ou Docker ausente recebem `UNVERIFIED`. O runner nunca infere aprovação por substring ou pela ausência de erro.

Essa validação reduz a superfície de confusão, mas não substitui a classificação baseada em observação independente do kernel. A próxima etapa deve substituir marcadores declarados pelo candidato por probes com ação concreta, sentinels protegidos e observação do runtime.

Os resultados podem ser registrados no `AttackMatrix`, cujo gate exige cobertura completa e rejeita qualquer `UNVERIFIED` ou `DETECTED`. Os testes atuais usam runner simulado para validar a lógica. A execução dos probes de escape contra Docker real continua pendente e não é simulada por estes testes.
