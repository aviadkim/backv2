"""
Services module initialization.
"""
from .document_service import DocumentService
from .database_service import DatabaseService
from .web_service import WebService

__all__ = [
    'DocumentService',
    'DatabaseService',
    'WebService'
]
