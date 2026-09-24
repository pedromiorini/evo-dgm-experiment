# Integridade antes de operações críticas

A base agora possui uma barreira explícita para operações como gerar mutação, promover variante, abrir FINAL ou executar replay crítico.

`verify_before_critical_operation()` verifica o hash determinístico do código do kernel, a cadeia do `KernelLog` persistente e quatro checks obrigatórios: `manifest_hash`, `dependency_hash`, `permissions` e `evaluator_state`. Um check ausente ou que retorne falso produz `CriticalIntegrityError` e bloqueia a operação.

O relatório só é emitido quando todas as verificações passam. A cadeia de logs continua classificada como `TAMPER_EVIDENT_LOCAL_ONLY`; a verificação não afirma imutabilidade nem substitui uma âncora externa independente.

A função é um componente de controle e ainda não está conectada a um executor de genoma. Essa separação é intencional: a execução permanece bloqueada enquanto o sandbox de produção não estiver disponível e validado.
