# EthiCore/__init__.py
# لجعل المجلد EthiCore قابلاً للاستيراد كمكتبة Python.

from .InferenceEngine import InferenceEngine
from .EthicalNetsModel import EthicalNetsModel
from .ContextualClassifier import ContextualClassifier

__all__ = [
    "InferenceEngine",
    "EthicalNetsModel",
    "ContextualClassifier",
]
