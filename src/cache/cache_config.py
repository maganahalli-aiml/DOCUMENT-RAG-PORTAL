"""
Cache configuration for Document RAG Portal
"""

# Cache settings
CACHE_CONFIG = {
    # Cache type: 'memory', 'sqlite', 'redis'
    "type": "memory",
    
    # Cache directory for persistent storage
    "directory": "cache",
    
    # Memory cache settings
    "memory": {
        "max_size": 1000,  # Maximum number of cached entries
        "ttl": 3600,       # Time to live in seconds (1 hour)
    },
    
    # SQLite cache settings  
    "sqlite": {
        "database_path": "cache/langchain_cache.db",
        "ttl": 86400,  # Time to live in seconds (24 hours)
    },
    
    # Cache behavior
    "behavior": {
        "enable_llm_cache": True,      # Cache LLM responses
        "enable_embedding_cache": True, # Cache embedding results
        "enable_retrieval_cache": True, # Cache retrieval results
        "cache_similar_queries": True,  # Cache semantically similar queries
    },
    
    # Performance settings
    "performance": {
        "similarity_threshold": 0.95,  # Threshold for considering queries similar
        "max_cache_size_mb": 100,      # Maximum cache size in MB
        "cleanup_interval": 3600,      # Cache cleanup interval in seconds
    }
}

# Environment-specific overrides
DEVELOPMENT_CACHE = {
    "type": "memory",
    "memory": {"max_size": 500, "ttl": 1800}  # Smaller cache for development
}

PRODUCTION_CACHE = {
    "type": "sqlite",
    "sqlite": {"ttl": 172800}  # 2 days TTL for production
}
