# Sentinels de acesso efetivo

A milestone de sentinels adiciona um registro kernel-only e um `SentinelWorkspace` físico para testes de exposição real. Cada sentinel recebe um segredo aleatório mantido somente no domínio confiável; o registro público contém apenas identificador e path protegido, nunca o segredo nem seu digest.

O workspace é criado em diretório temporário fora do projeto, com diretório `0700` e arquivo sentinel `0600`. A limpeza é determinística via context manager e o sentinel **não é montado nem copiado para o container avaliado**. Assim, a presença do arquivo no host não é confundida com sua exposição ao candidato.

A classificação não depende de `path.exists()`:

- nenhuma tentativa de acesso → `BLOCKED`;
- abertura com digest do segredo correto → `DETECTED`;
- abertura sem digest verificável → `UNVERIFIED`;
- observação inconsistente → erro fail-closed.

O componente ainda não executa candidatos nem conecta automaticamente cada sentinel aos 13 probes. A próxima etapa deve fornecer uma ação adversarial concreta, executar o container aprovado, observar o resultado fora do stdout declarativo e registrar cada resultado na matriz. Até que isso ocorra, o workspace é evidência de engenharia, não evidência de isolamento operacional.
