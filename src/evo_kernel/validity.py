"""Estados de validade separados de promoção operacional."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ValidityState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"
    FUNCTIONALLY_VALID = "FUNCTIONALLY_VALID"
    SECURITY_VALID = "SECURITY_VALID"
    EXPERIMENTALLY_VALID = "EXPERIMENTALLY_VALID"
    PROMOTED = "PROMOTED"
    FAILED_SECURITY = "FAILED_SECURITY"
    FAILED_PROTOCOL = "FAILED_PROTOCOL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class PromotionDenied(RuntimeError):
    """Candidato não satisfaz os invariantes para promoção."""


@dataclass(frozen=True)
class CandidateValidity:
    functional: bool = False
    security: bool = False
    experimental: bool = False
    critical_regression: bool = False

    @property
    def state(self) -> ValidityState:
        if self.critical_regression:
            return ValidityState.FAILED_SECURITY
        if self.functional and self.security and self.experimental:
            return ValidityState.PROMOTED
        if self.experimental:
            return ValidityState.EXPERIMENTALLY_VALID
        if self.security:
            return ValidityState.SECURITY_VALID
        if self.functional:
            return ValidityState.FUNCTIONALLY_VALID
        return ValidityState.NOT_EXECUTED

    def require_promotion(self) -> None:
        if self.critical_regression:
            raise PromotionDenied("regressão crítica impede promoção")
        if not (self.functional and self.security and self.experimental):
            raise PromotionDenied("promoção exige validade funcional, de segurança e experimental")
