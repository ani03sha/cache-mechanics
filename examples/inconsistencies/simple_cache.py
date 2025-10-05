"""
Simple TTL Based Cache Implementation

A basic cache where entries automatically expire after a specified time period.
This example demonstrates core TTL concepts for educational purposes.
"""

import time
from typing import Any, Optional

class SimpleCache:
    
    def __init__(self, default_ttl: float = 60.0):
        """
        Initialize cache

        Args:
            default_ttl: Default time-to-live in seconds for cache entries
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expiration_time = time.time() + (ttl if ttl is not None else self._default_ttl)
        self._cache[key] = {
            "value": value,
            "expires_at": expiration_time
        }

    def get(self, key: str) -> Optional[Any]:
        if not self.__contains__(key):
            return None
        
        entry = self._cache[key]

        # Check if key has expired
        if time.time() > entry["expires_at"]:
            # Lazy deletion: remove expired entry on access
            del self._cache[key]
            return None

        return entry["value"]
    
    def delete(self, key: str) -> bool:
        if self.__contains__(key):
            del self._cache[key]
            return True
        
        return False
    
    def clear(self):
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        return key in self._cache
    

if __name__ == "__main__":
    # Example usage                                                                                                                    
    print("TTL Cache Example\n" + "=" * 50)                                                                                            
                                                                                                                                       
    cache = SimpleCache(default_ttl=2.0)  # 2 second default TTL                                                                          
                                                                                                                                       
    # Store some values                                                                                                                
    cache.set("user:123", {"name": "Alice", "role": "admin"})                                                                          
    cache.set("session:abc", "active", ttl=1.0)  # Custom 1 second TTL                                                                 
                                                                                                                                       
    print(f"Stored 2 entries, cache size: {len(cache)}")                                                                               
    print(f"user:123 = {cache.get('user:123')}")                                                                                       
    print(f"session:abc = {cache.get('session:abc')}")                                                                                 
                                                                                                                                       
    # Wait for session to expire                                                                                                       
    print("\nWaiting 1.5 seconds...")                                                                                                  
    time.sleep(1.5)                                                                                                                    
                                                                                                                                       
    print(f"user:123 = {cache.get('user:123')} (should still be valid)")                                                               
    print(f"session:abc = {cache.get('session:abc')} (should be expired)")                                                             
                                                                                                                                       
    # Wait for user to expire                                                                                                          
    print("\nWaiting another 1 second...")                                                                                             
    time.sleep(1.0)                                                                                                                    
                                                                                                                                       
    print(f"user:123 = {cache.get('user:123')} (should be expired)")