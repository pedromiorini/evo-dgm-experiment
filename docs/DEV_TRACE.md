# DEV_TRACE — PATCH 7

O `DEV_TRACE` registra feedback descritivo de desenvolvimento sem transformar conteúdo histórico em instrução confiável.

Cada entrada possui:

- `source_variant_id`;
- `generation`;
- `producer`;
- conteúdo sanitizado e limitado a 4096 caracteres;
- `content_hash`;
- timestamp;
- `trust_class=UNTRUSTED_DATA`.

Padrões comuns de credenciais são redigidos. Campos de `selection`, `final`, `holdout`, `credentials` e `secrets` são rejeitados na fronteira, pois não pertencem ao trace descritivo. O texto adversarial restante é preservado como **dado**, não como comando.

A serialização para histórico não contém campos de política, orçamento, seleção, holdout ou autoridade operacional. O módulo não chama LLM, não executa código e não promove variantes.
