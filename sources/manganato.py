import re
from typing import List
from urllib.parse import quote
from .base import BaseMangaSource
from models.schemas import (
    SearchResult, MangaDetails, Chapter, ChapterPages,
    PopularManga, MangaStatus
)

class ManganatoSource(BaseMangaSource):
    def __init__(self):
        super().__init__()
        self.name = "Manganato"
        self.base_url = "https://manganato.com"
        self.chapbase_url = "https://chapmanganato.to"
        self.icon = f"{self.base_url}/favicon.ico"
        self.language = "en"
    
    async def search(self, query: str, page: int = 1) -> List[SearchResult]:
        """Search for manga"""
        try:
            search_query = query.replace(" ", "_")
            url = f"{self.base_url}/search/story/{quote(search_query)}?page={page}"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            items = soup.select(".search-story-item")
            
            for item in items:
                link = item.select_one("a.item-img")
                title = item.select_one("a.item-title")
                img = item.select_one("img")
                chapter = item.select_one(".item-chapter a")
                
                if link and title:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(SearchResult(
                        id=manga_id,
                        title=title.get_text(strip=True),
                        cover=img.get("src") if img else None,
                        url=manga_url,
                        source="manganato",
                        latest_chapter=chapter.get_text(strip=True) if chapter else None
                    ))
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def get_manga_details(self, manga_id: str) -> MangaDetails:
        """Get manga details"""
        try:
            url = f"{self.chapbase_url}/manga-{manga_id}"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            # Title and cover
            title = soup.select_one("h1")
            cover = soup.select_one(".info-image img")
            desc = soup.select_one("#panel-story-info-description")
            
            # Metadata
            author = artist = status = None
            genres = []
            
            info_table = soup.select(".variations-tableInfo tr")
            for row in info_table:
                label = row.select_one(".table-label")
                value = row.select_one(".table-value")
                if label and value:
                    label_text = label.get_text(strip=True).lower()
                    if "author" in label_text:
                        author = value.get_text(strip=True)
                    elif "status" in label_text:
                        status = self._parse_status(value.get_text(strip=True))
                    elif "genres" in label_text:
                        genres = [a.get_text(strip=True) for a in value.select("a")]
            
            # Chapters
            chapters = []
            chapter_list = soup.select(".row-content-chapter li")
            
            for ch in chapter_list:
                ch_link = ch.select_one("a")
                ch_date = ch.select_one(".chapter-time")
                
                if ch_link:
                    ch_url = ch_link.get("href", "")
                    ch_id = self._extract_chapter_id(ch_url)
                    ch_title = ch_link.get_text(strip=True)
                    ch_number = self._extract_chapter_number(ch_title)
                    
                    chapters.append(Chapter(
                        id=ch_id,
                        number=ch_number,
                        title=ch_title,
                        url=ch_url,
                        release_date=ch_date.get("title") if ch_date else None
                    ))
            
            return MangaDetails(
                id=manga_id,
                title=title.get_text(strip=True) if title else manga_id,
                cover=cover.get("src") if cover else None,
                description=desc.get_text(strip=True) if desc else None,
                author=author,
                artist=artist,
                status=status,
                genres=genres,
                source="manganato",
                url=url,
                chapters=chapters,
                total_chapters=len(chapters)
            )
        except Exception as e:
            print(f"Details error: {e}")
            raise
    
    async def get_chapter_pages(self, chapter_id: str) -> ChapterPages:
        """Get chapter pages"""
        try:
            url = chapter_id if chapter_id.startswith("http") else f"{self.chapbase_url}/{chapter_id}"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            pages = []
            images = soup.select(".container-chapter-reader img")
            
            for img in images:
                src = img.get("src")
                if src:
                    pages.append(src)
            
            title = soup.select_one(".panel-chapter-info-top h1")
            ch_number = self._extract_chapter_number(
                title.get_text(strip=True) if title else chapter_id
            )
            
            return ChapterPages(
                chapter_id=chapter_id,
                chapter_number=ch_number,
                title=title.get_text(strip=True) if title else None,
                pages=pages,
                total_pages=len(pages)
            )
        except Exception as e:
            print(f"Chapter pages error: {e}")
            raise
    
    async def get_popular(self, page: int = 1) -> List[PopularManga]:
        """Get popular manga"""
        try:
            url = f"{self.base_url}/genre-all/{page}?type=topview"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            items = soup.select(".content-genres-item")
            
            for item in items:
                link = item.select_one("a.genres-item-img")
                title = item.select_one("a.genres-item-name")
                img = item.select_one("img")
                
                if link and title:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(PopularManga(
                        id=manga_id,
                        title=title.get_text(strip=True),
                        cover=img.get("src") if img else "",
                        url=manga_url,
                        source="manganato"
                    ))
            
            return results
        except Exception as e:
            print(f"Popular error: {e}")
            return []
    
    async def get_latest(self, page: int = 1) -> List[SearchResult]:
        """Get latest manga"""
        try:
            url = f"{self.base_url}/genre-all/{page}"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            items = soup.select(".content-genres-item")
            
            for item in items:
                link = item.select_one("a.genres-item-img")
                title = item.select_one("a.genres-item-name")
                img = item.select_one("img")
                chapter = item.select_one(".genres-item-chap")
                
                if link and title:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(SearchResult(
                        id=manga_id,
                        title=title.get_text(strip=True),
                        cover=img.get("src") if img else None,
                        url=manga_url,
                        source="manganato",
                        latest_chapter=chapter.get_text(strip=True) if chapter else None
                    ))
            
            return results
        except Exception as e:
            print(f"Latest error: {e}")
            return []
    
    # ============ Helpers ============
    def _extract_id(self, url: str) -> str:
        match = re.search(r'manga-(\w+)', url)
        return match.group(1) if match else url
    
    def _extract_chapter_id(self, url: str) -> str:
        return url
    
    def _extract_chapter_number(self, text: str) -> float:
        match = re.search(r'chapter[^\d]*(\d+(?:\.\d+)?)', text.lower())
        return float(match.group(1)) if match else 0.0
    
    def _parse_status(self, status: str) -> MangaStatus:
        status_lower = status.lower()
        if "ongoing" in status_lower:
            return MangaStatus.ONGOING
        elif "completed" in status_lower:
            return MangaStatus.COMPLETED
        return MangaStatus.ONGOING
