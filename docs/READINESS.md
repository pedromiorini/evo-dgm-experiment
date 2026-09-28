# Relatório de prontidão

`RuntimeReadiness` mantém separados três gates: `policy_ready`, que indica apenas que o perfil declarativo é válido; `runtime_verified`, que exige evidência guardada pelo `DockerExecutor`; e `attacks_verified`, que exige uma `AttackMatrix` completa sem `UNVERIFIED`.

`execution_authorized` só é verdadeiro quando os três gates passam. O relatório inclui bloqueadores explícitos e pode ser serializado sem executar Docker, probes ou código de genoma. Assim, uma política bem escrita, uma matriz mockada ou um runtime indisponível não fabricam autorização.

No ambiente atual, a política pode estar pronta, mas o processo experimental não tem acesso ao socket Docker; além disso, a inspeção do daemon não mostrou rootless/userns. Docker instalado e serviço ativo não são runtime verificado. Os ataques reais também não têm evidência. O relatório deve permanecer `FAIL_CLOSED` até a boundary ser escolhida, configurada e validada operacionalmente.
