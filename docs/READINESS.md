# Relatório de prontidão

`RuntimeReadiness` mantém separados três gates: `policy_ready`, que indica apenas que o perfil declarativo é válido; `runtime_verified`, que exige evidência guardada pelo `DockerExecutor`; e `attacks_verified`, que exige uma `AttackMatrix` completa sem `UNVERIFIED`.

`execution_authorized` só é verdadeiro quando os três gates passam. O relatório inclui bloqueadores explícitos e pode ser serializado sem executar Docker, probes ou código de genoma. Assim, uma política bem escrita, uma matriz mockada ou um runtime indisponível não fabricam autorização.

No ambiente atual, a política pode estar pronta, mas Docker não está disponível e os ataques reais ainda não têm evidência. O relatório deve permanecer `FAIL_CLOSED` até a validação operacional.
