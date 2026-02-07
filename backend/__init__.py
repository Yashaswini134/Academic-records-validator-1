"""
Backend Module for Certificate Verification System
Orchestrates OCR, Hash, and Decision Engine components
"""

from .main_controller import CertificateVerificationController
from .decision_engine import DecisionEngine

__all__ = ['CertificateVerificationController', 'DecisionEngine']
