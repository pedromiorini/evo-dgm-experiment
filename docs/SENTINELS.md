# Sentinels de acesso efetivo

A milestone de sentinels adiciona um registro kernel-only para testes de exposição real. Cada sentinel recebe um segredo aleatório mantido somente no domínio confiável; o registro público contém apenas identificador e path protegido, nunca o segredo nem seu digest.

A classificação não depende de `path.exists()`:

- nenhuma tentativa de acesso → `BLOCKED`;
- abertura com digest do segredo correto → `DETECTED`;
- abertura sem digest verificável → `UNVERIFIED`;
- observação inconsistente → erro fail-closed.

O componente ainda não cria automaticamente sentinels fora do filesystem do container nem executa candidatos. Ele fornece o contrato de observação para a próxima etapa, que deverá criar sentinels reais no domínio protegido, executar uma tentativa adversarial no container e devolver ao kernel somente observações verificáveis.
