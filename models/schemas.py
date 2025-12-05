from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

# ============ Enums ============
class SourceType(str, Enum):
    ASURASCANS = "asurascans"
    FLAMESCANS = "flamescans"
    REAPERSCANS = "reaperscans"
    MANGANATO = "manganato"
    MANGADEX = "mangadex"

class MangaStatus(str, Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    HIATUS = "hiatus"
    CANCELLED = "cancelled"

class DownloadFormat(str, Enum):
    PDF = "pdf"
    CBZ = "cbz"
    ZIP = "zip"
    IMAGES = "images"

# ============ Base Models ============
class SourceInfo(BaseModel):
    id: str
    name: str
    url: str
    icon: Optional[str] = None
    language: str = "en"
    is_active: bool = True

class SearchResult(BaseModel):
    id: str
    title: str
    cover: Optional[str] = None
    url: str
    source: str
    latest_chapter: Optional[str] = None

class Chapter(BaseModel):
    id: str
    number: float
    title: Optional[str] = None
    url: str
    release_date: Optional[str] = None
    scanlator: Optional[str] = None

class ChapterPages(BaseModel):
    chapter_id: str
    chapter_number: float
    title: Optional[str] = None
    pages: List[str]  # List of image URLs
    total_pages: int

class MangaDetails(BaseModel):
    id: str
    title: str
    alternative_titles: List[str] = []
    cover: Optional[str] = None
    banner: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[MangaStatus] = None
    genres: List[str] = []
    tags: List[str] = []
    rating: Optional[float] = None
    views: Optional[int] = None
    source: str
    url: str
    chapters: List[Chapter] = []
    total_chapters: int = 0

class DownloadRequest(BaseModel):
    source: str
    chapter_id: str
    format: DownloadFormat = DownloadFormat.PDF

class DownloadResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None

class PopularManga(BaseModel):
    id: str
    title: str
    cover: str
    url: str
    source: str
    rating: Optional[float] = None
    views: Optional[int] = None

# ============ API Responses ============
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    success: bool = True
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[dict]
