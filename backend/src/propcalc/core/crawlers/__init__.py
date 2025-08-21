"""
Property Web Crawlers Module for PropCalc
Implements ethical and legal web scraping for real estate websites
"""

__version__ = "2.1.0"
__author__ = "PropCalc Team"

from .base_crawler import BaseCrawler
from .property_finder_crawler import PropertyFinderCrawler
from .bayut_crawler import BayutCrawler
from .crawler_manager import CrawlerManager

__all__ = [
    "BaseCrawler",
    "PropertyFinderCrawler", 
    "BayutCrawler",
    "CrawlerManager"
]
