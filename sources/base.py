from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
import cloudscraper
from bs4 import BeautifulSoup
import asyncio
from models.schemas import (
    SearchResult, MangaDetails, Chapter, ChapterPages, PopularManga
)

class BaseMangaSource(ABC):
    """Abstract base class for all manga sources"""
    
    def __init__(self):
        self.name: str = ""
        self.base_url: str = ""
        self.icon: str = ""
        self.language: str = "en"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.scraper = cloudscraper.create_scraper()
    
    async def fetch(self, url: str) -> str:
        """Fetch page content"""
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    
    def fetch_sync(self, url: str) -> str:
        """Synchronous fetch using cloudscraper (for Cloudflare)"""
        response = self.scraper.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')
    
    @abstractmethod
    async def search(self, query: str, page: int = 1) -> List[SearchResult]:
        """Search for manga"""
        pass
    
    @abstractmethod
    async def get_manga_details(self, manga_id: str) -> MangaDetails:
        """Get manga details and chapter list"""
        pass
    
    @abstractmethod
    async def get_chapter_pages(self, chapter_id: str) -> ChapterPages:
        """Get all pages for a chapter"""
        pass
    
    @abstractmethod
    async def get_popular(self, page: int = 1) -> List[PopularManga]:
        """Get popular manga"""
        pass
    
    @abstractmethod
    async def get_latest(self, page: int = 1) -> List[SearchResult]:
        """Get latest updated manga"""
        pass
    
    def get_source_info(self) -> dict:
        """Get source information"""
        return {
            "id": self.__class__.__name__.lower().replace("source", ""),
            "name": self.name,
            "url": self.base_url,
            "icon": self.icon,
            "language": self.language,
            "is_active": True
        }
