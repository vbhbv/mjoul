
# EthiCore/__init__.py
# لجعل المجلد EthiCore قابلاً للاستيراد كمكتبة Python.

from .InferenceEngine import InferenceEngine
from .EthicalNetsModel import EthicalNetsModel
from .ContextualClassifier import ContextualClassifier

# تحديد ما يتم استيراده تلقائيًا عند استخدام 'from EthiCore import *'
__all__ = [
    "InferenceEngine",
    "EthicalNetsModel",
    "ContextualClassifier",
]
