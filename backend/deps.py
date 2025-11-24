# backend/deps.py
from storage import storage
from typing import Dict

# For backward compatibility with existing routers
_sessions_cache: Dict = {}
_datasets_cache: Dict = {}

def get_sessions():
    """Dependency for accessing sessions"""
    return _sessions_cache

def get_datasets():
    """Dependency for accessing datasets"""
    return _datasets_cache

def get_storage():
    """Dependency for accessing storage"""
    return storage