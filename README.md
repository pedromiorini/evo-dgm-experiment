# Sistema Experimental de Auto-Modificação Evolutiva

Projeto experimental inspirado na Darwin Gödel Machine para investigar, sob protocolo auditável, se a auto-modificação evolutiva produz melhoria funcional generalizável sem regressão crítica de segurança, validade ou custo.

> **Estado atual: `NOT_STARTED` — Fase F1 (protocolo e decisões humanas).**
>
> O kernel experimental ainda **não deve ser implementado**. A especificação exige que as decisões metodológicas, de segurança e de governança sejam explicitadas e aprovadas antes da implementação.

## Documentos principais

- [Especificação completa](docs/SPEC.md)
- [Modelo de ameaças](docs/THREAT_MODEL.md)
- [Decisões humanas pendentes](protocol/DECISOES_HUMANAS.md)
- [Arquitetura e fronteiras de confiança](protocol/ARQUITETURA.md)
- [Plano de protocolo F1](protocol/PLANO_F1.md)

## Princípios operacionais

1. O kernel é confiável e o genoma é não confiável.
2. Segurança é implementada por código, permissões e ambiente; prompt não é boundary.
3. Holdout, evaluator, seleção, orçamento, manifesto e logs oficiais permanecem sob controle do kernel.
4. Conteúdo histórico entre gerações é sempre `UNTRUSTED_DATA`, nunca instrução.
5. O sistema falha fechado quando uma propriedade crítica não puder ser verificada.
6. `INSUFFICIENT_EVIDENCE` é um resultado válido.
7. O projeto não faz alegações sobre consciência, experiência subjetiva, identidade, vida ou agência psicológica.

## Desenvolvimento

O projeto será implementado em Python 3.12+ quando a F1 for concluída e as decisões humanas necessárias forem registradas em `pending_approval/`. Até lá, alterações devem ser limitadas à documentação, ao protocolo e aos artefatos de revisão.

```bash
python3 --version
git status
```

Não execute um experimento confirmatório a partir deste repositório enquanto o estado global não tiver sido alterado por decisão humana documentada.

## Licença

A licença ainda não foi escolhida. Essa é uma das decisões de governança a registrar antes da publicação pública.
