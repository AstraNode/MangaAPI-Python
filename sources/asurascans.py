import re
from typing import List
from urllib.parse import urljoin, quote
from .base import BaseMangaSource
from models.schemas import (
    SearchResult, MangaDetails, Chapter, ChapterPages, 
    PopularManga, MangaStatus
)

class AsuraScansSource(BaseMangaSource):
    def __init__(self):
        super().__init__()
        self.name = "Asura Scans"
        self.base_url = "https://asuracomic.net"  # Update if changed
        self.icon = f"{self.base_url}/favicon.ico"
        self.language = "en"
    
    async def search(self, query: str, page: int = 1) -> List[SearchResult]:
        """Search for manga on Asura Scans"""
        try:
            url = f"{self.base_url}/?s={quote(query)}"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            manga_items = soup.select(".listupd .bs")
            
            for item in manga_items:
                link = item.select_one("a")
                img = item.select_one("img")
                title_elem = item.select_one(".tt")
                chapter = item.select_one(".epxs")
                
                if link and title_elem:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(SearchResult(
                        id=manga_id,
                        title=title_elem.get_text(strip=True),
                        cover=img.get("src") if img else None,
                        url=manga_url,
                        source="asurascans",
                        latest_chapter=chapter.get_text(strip=True) if chapter else None
                    ))
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def get_manga_details(self, manga_id: str) -> MangaDetails:
        """Get manga details from Asura Scans"""
        try:
            url = f"{self.base_url}/manga/{manga_id}/"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            # Extract info
            title = soup.select_one(".entry-title")
            cover = soup.select_one(".thumb img")
            desc = soup.select_one(".entry-content[itemprop='description']")
            
            # Extract metadata
            info_items = soup.select(".infox .fmed")
            author = artist = status = None
            genres = []
            
            for item in info_items:
                label = item.select_one("b")
                value = item.select_one("span")
                if label and value:
                    label_text = label.get_text(strip=True).lower()
                    value_text = value.get_text(strip=True)
                    
                    if "author" in label_text:
                        author = value_text
                    elif "artist" in label_text:
                        artist = value_text
                    elif "status" in label_text:
                        status = self._parse_status(value_text)
            
            # Extract genres
            genre_links = soup.select(".mgen a")
            genres = [g.get_text(strip=True) for g in genre_links]
            
            # Extract chapters
            chapters = []
            chapter_items = soup.select("#chapterlist li")
            
            for ch in chapter_items:
                ch_link = ch.select_one("a")
                ch_num = ch.select_one(".chapternum")
                ch_date = ch.select_one(".chapterdate")
                
                if ch_link:
                    ch_url = ch_link.get("href", "")
                    ch_id = self._extract_chapter_id(ch_url)
                    ch_number = self._extract_chapter_number(
                        ch_num.get_text(strip=True) if ch_num else ""
                    )
                    
                    chapters.append(Chapter(
                        id=ch_id,
                        number=ch_number,
                        title=ch_num.get_text(strip=True) if ch_num else None,
                        url=ch_url,
                        release_date=ch_date.get_text(strip=True) if ch_date else None
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
                source="asurascans",
                url=url,
                chapters=chapters,
                total_chapters=len(chapters)
            )
        except Exception as e:
            print(f"Details error: {e}")
            raise
    
    async def get_chapter_pages(self, chapter_id: str) -> ChapterPages:
        """Get chapter pages from Asura Scans"""
        try:
            url = f"{self.base_url}/{chapter_id}/"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            # Extract images
            pages = []
            img_containers = soup.select("#readerarea img")
            
            for img in img_containers:
                src = img.get("src") or img.get("data-src")
                if src and not "logo" in src.lower():
                    pages.append(src)
            
            # Extract chapter info
            title = soup.select_one(".entry-title")
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
            url = f"{self.base_url}/manga/?page={page}&order=popular"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            manga_items = soup.select(".listupd .bs")
            
            for item in manga_items:
                link = item.select_one("a")
                img = item.select_one("img")
                title_elem = item.select_one(".tt")
                rating = item.select_one(".rating .num")
                
                if link and title_elem:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(PopularManga(
                        id=manga_id,
                        title=title_elem.get_text(strip=True),
                        cover=img.get("src") if img else "",
                        url=manga_url,
                        source="asurascans",
                        rating=float(rating.get_text(strip=True)) if rating else None
                    ))
            
            return results
        except Exception as e:
            print(f"Popular error: {e}")
            return []
    
    async def get_latest(self, page: int = 1) -> List[SearchResult]:
        """Get latest updated manga"""
        try:
            url = f"{self.base_url}/manga/?page={page}&order=update"
            html = self.fetch_sync(url)
            soup = self.parse_html(html)
            
            results = []
            manga_items = soup.select(".listupd .bs")
            
            for item in manga_items:
                link = item.select_one("a")
                img = item.select_one("img")
                title_elem = item.select_one(".tt")
                chapter = item.select_one(".epxs")
                
                if link and title_elem:
                    manga_url = link.get("href", "")
                    manga_id = self._extract_id(manga_url)
                    
                    results.append(SearchResult(
                        id=manga_id,
                        title=title_elem.get_text(strip=True),
                        cover=img.get("src") if img else None,
                        url=manga_url,
                        source="asurascans",
                        latest_chapter=chapter.get_text(strip=True) if chapter else None
                    ))
            
            return results
        except Exception as e:
            print(f"Latest error: {e}")
            return []
    
    # ============ Helper Methods ============
    def _extract_id(self, url: str) -> str:
        """Extract manga ID from URL"""
        match = re.search(r'/manga/([^/]+)', url)
        return match.group(1) if match else url
    
    def _extract_chapter_id(self, url: str) -> str:
        """Extract chapter ID from URL"""
        match = re.search(r'/([^/]+)/?$', url.rstrip('/'))
        return match.group(1) if match else url
    
    def _extract_chapter_number(self, text: str) -> float:
        """Extract chapter number from text"""
        match = re.search(r'chapter[^\d]*(\d+(?:\.\d+)?)', text.lower())
        if match:
            return float(match.group(1))
        return 0.0
    
    def _parse_status(self, status: str) -> MangaStatus:
        """Parse manga status"""
        status_lower = status.lower()
        if "ongoing" in status_lower:
            return MangaStatus.ONGOING
        elif "completed" in status_lower:
            return MangaStatus.COMPLETED
        elif "hiatus" in status_lower:
            return MangaStatus.HIATUS
        return MangaStatus.ONGOING
