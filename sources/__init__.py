from typing import Dict, Optional
from .base import BaseMangaSource
from .asurascans import AsuraScansSource
from .manganato import ManganatoSource

# Registry of all available sources
SOURCES: Dict[str, BaseMangaSource] = {
    "asurascans": AsuraScansSource(),
    "manganato": ManganatoSource(),
    # Add more sources here
}

def get_source(source_id: str) -> Optional[BaseMangaSource]:
    """Get a source by its ID"""
    return SOURCES.get(source_id.lower())

def get_all_sources() -> Dict[str, BaseMangaSource]:
    """Get all available sources"""
    return SOURCES

def list_sources() -> list:
    """List all source IDs"""
    return list(SOURCES.keys())
