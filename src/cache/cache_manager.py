"""
LangChain Cache Manager for Document RAG Portal
Provides in-memory and persistent caching for LLM responses and embeddings.
"""

import os
import sys
from typing import Optional, Dict, Any
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class CacheManager:
    """
    Manages LangChain caching strategies for optimal performance.
    """
    
    def __init__(self, cache_type: str = "memory", cache_dir: str = "cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_type: Type of cache ('memory', 'sqlite', 'redis')
            cache_dir: Directory for persistent cache files
        """
        self.log = CustomLogger().get_logger(__name__)
        self.cache_type = cache_type
        self.cache_dir = cache_dir
        self.cache_instance = None
        
        # Ensure cache directory exists
        if cache_type in ['sqlite']:
            os.makedirs(cache_dir, exist_ok=True)
        
        self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize the appropriate cache type."""
        try:
            if self.cache_type == "memory":
                self.cache_instance = InMemoryCache()
                self.log.info("Initialized InMemoryCache for LangChain")
                
            elif self.cache_type == "sqlite":
                cache_file = os.path.join(self.cache_dir, "langchain_cache.db")
                self.cache_instance = SQLiteCache(database_path=cache_file)
                self.log.info(f"Initialized SQLiteCache at {cache_file}")
                
            else:
                # Fallback to memory cache
                self.cache_instance = InMemoryCache()
                self.log.warning(f"Unsupported cache type '{self.cache_type}', falling back to memory cache")
            
            # Set global LangChain cache
            set_llm_cache(self.cache_instance)
            self.log.info(f"LangChain cache activated: {self.cache_type}")
            
        except Exception as e:
            self.log.error(f"Failed to initialize cache: {str(e)}")
            raise DocumentPortalException("Cache initialization failed", sys)
    
    def clear_cache(self):
        """Clear all cached entries."""
        try:
            if hasattr(self.cache_instance, 'clear'):
                self.cache_instance.clear()
                self.log.info("Cache cleared successfully")
            else:
                self.log.warning("Cache instance does not support clearing")
        except Exception as e:
            self.log.error(f"Failed to clear cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics if available."""
        try:
            stats = {
                "cache_type": self.cache_type,
                "cache_enabled": self.cache_instance is not None
            }
            
            # Add specific stats if available
            if hasattr(self.cache_instance, '__len__'):
                stats["cache_size"] = len(self.cache_instance)
            
            return stats
            
        except Exception as e:
            self.log.error(f"Failed to get cache stats: {str(e)}")
            return {"cache_type": self.cache_type, "error": str(e)}
    
    def get_cache_info(self) -> str:
        """Get human-readable cache information."""
        stats = self.get_cache_stats()
        info = f"Cache Type: {stats.get('cache_type', 'unknown')}\n"
        info += f"Cache Enabled: {stats.get('cache_enabled', False)}\n"
        
        if 'cache_size' in stats:
            info += f"Cached Entries: {stats['cache_size']}\n"
        
        return info

# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager(cache_type: str = "memory") -> CacheManager:
    """
    Get or create the global cache manager instance.
    
    Args:
        cache_type: Type of cache to use
        
    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None or _cache_manager.cache_type != cache_type:
        _cache_manager = CacheManager(cache_type=cache_type)
    
    return _cache_manager

def initialize_langchain_cache(cache_type: str = "memory") -> CacheManager:
    """
    Initialize LangChain caching for the application.
    
    Args:
        cache_type: Type of cache ('memory', 'sqlite')
        
    Returns:
        CacheManager instance
    """
    return get_cache_manager(cache_type)

def clear_langchain_cache():
    """Clear the LangChain cache."""
    global _cache_manager
    if _cache_manager:
        _cache_manager.clear_cache()
