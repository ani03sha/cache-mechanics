"""                                                                                                                                    
Concurrent Writes - Demonstrating Stale Data in Caches                                                                                 
                                                                                                                                        
This example shows how concurrent write operations can lead to cache inconsistencies                                                   
and stale data when multiple threads update the same cache entry.                                                                      
"""

import threading
import time
from typing import Any, Optional
from simple_cache import SimpleCache


def simulate_database_write(key: str, value: Any, delay: float = 0.1) -> None:
    "Simulate a slow database write operation"
    time.sleep(delay)
    print(f" [DB] wrote {key} = {value}")

def update_with_cache(cache: SimpleCache, key: str, value: Any, write_delay: float, thread_name: str) -> None:
    """                                                                                                                                
    Update both database and cache (write-through pattern).                                                                            
                                                                                                                                       
    Common pattern: Write to DB first, then update cache.                                                                              
    Problem: Race conditions can cause stale data!                                                                                     
    """                                                                                                                                
    print(f"[{thread_name}] Starting update: {key} = {value}")                                                                         
                                                                                                                                       
    # Step 1: Write to database (slow operation)                                                                                       
    simulate_database_write(key, value, delay=write_delay)                                                                             
                                                                                                                                       
    # Step 2: Update cache
    cache.set(key, value)

    print(f"[{thread_name}] Completed update: {key} = {value}")


def scenario_1_race_condition():
    """
    Scenario 1: Last write win race condition

    Two threads update the same key with different values.
    The thread that updates the cache LAST wins, even if wrote to the DB first
    (creating DB-cache inconsistency)
    """
    print("\n" + "=" * 70)                                                                                                             
    print("SCENARIO 1: Race Condition - Last Write Wins")                                                                              
    print("=" * 70)

    cache = SimpleCache(default_ttl=10.0)

    # Initial state
    cache.set("user:123:status", "offline")
    print(f"Initial cache state: user:123:status = {cache.get('user:123:status')}\n")

    # Thread 1: Quick DB write (0.1s) - starts first, finishes first                                                                   
    # Thread 2: Slow DB write (0.3s) - starts second, finishes second                                                                  
    # Expected in DB: "online" (Thread 1 wrote first)                                                                                  
    # Expected in cache: Should match DB, but might not due to race!                                                                   
                                                                                                                                       
    thread1 = threading.Thread(                                                                                                        
        target=update_with_cache,                                                                                                      
        args=(cache, "user:123:status", "online", 0.1, "Thread-1"),                                                                    
        name="Thread-1"                                                                                                                
    )                                                                                                                                  
                                                                                                                                       
    thread2 = threading.Thread(                                                                                                        
        target=update_with_cache,                                                                                                      
        args=(cache, "user:123:status", "away", 0.3, "Thread-2"),                                                                      
        name="Thread-2"                                                                                                                
    )                                                                                                                                  
                                                                                                                                       
    # Start both threads                                                                                                               
    thread1.start()                                                                                                                    
    time.sleep(0.05)  # Small delay to ensure Thread-1 starts first                                                                    
    thread2.start()                                                                                                                    
                                                                                                                                       
    # Wait for both to complete                                                                                                        
    thread1.join()                                                                                                                     
    thread2.join()                                                                                                                     
                                                                                                                                       
    print(f"\nFinal cache state: user:123:status = {cache.get('user:123:status')}")                                                    
    print("Expected DB state: 'online' (Thread-1 wrote first)")                                                                        
    print("Cache might show 'away' if Thread-2 updated cache last!")                                                                                                                               
                                                                                                                                       
def scenario_2_interleaved_updates():                                                                                                  
    """                                                                                                                                
    Scenario 2: Multiple Interleaved Updates                                                                                           
                                                                                                                                       
    Multiple threads updating different fields of the same entity.                                                                     
    Shows how partial updates can create inconsistent snapshots.                                                                       
    """                                                                                                                                
    print("\n" + "=" * 70)                                                                                                             
    print("SCENARIO 2: Interleaved Updates - Inconsistent Snapshots")                                                                  
    print("=" * 70)                                                                                                                    
                                                                                                                                       
    cache = SimpleCache(default_ttl=10.0)                                                                                              
                                                                                                                                       
    # Initial user state                                                                                                               
    user_data = {"name": "Alice", "email": "alice@old.com", "age": 25}                                                                 
    cache.set("user:456", user_data)                                                                                                   
    print(f"Initial state: {cache.get('user:456')}\n")                                                                                 
                                                                                                                                       
    def update_user_field(field: str, value: Any, delay: float, thread_name: str):                                                     
        """Update a single field in user data."""                                                                                      
        print(f"[{thread_name}] Updating {field} = {value}")                                                                           
                                                                                                                                       
        # Simulate DB write                                                                                                            
        time.sleep(delay)                                                                                                              
        print(f"  [DB] Updated user:456.{field} = {value}")                                                                            
                                                                                                                                       
        # Update cache - read-modify-write pattern                                                                                     
        current = cache.get("user:456") or {}                                                                                          
        current[field] = value                                                                                                         
        cache.set("user:456", current)                                                                                                 
                                                                                                                                       
        print(f"[{thread_name}] Cache updated")                                                                                        
                                                                                                                                       
    # Three concurrent updates to different fields                                                                                     
    threads = [                                                                                                                        
        threading.Thread(                                                                                                              
            target=update_user_field,                                                                                                  
            args=("email", "alice@new.com", 0.2, "Email-Thread"),                                                                      
            name="Email-Thread"                                                                                                        
        ),                                                                                                                             
        threading.Thread(                                                                                                              
            target=update_user_field,                                                                                                  
            args=("age", 26, 0.1, "Age-Thread"),                                                                                       
            name="Age-Thread"                                                                                                          
        ),                                                                                                                             
        threading.Thread(                                                                                                              
            target=update_user_field,                                                                                                  
            args=("name", "Alice Smith", 0.15, "Name-Thread"),                                                                         
            name="Name-Thread"                                                                                                         
        ),                                                                                                                             
    ]                                                                                                                                  
                                                                                                                                       
    for t in threads:                                                                                                                  
        t.start()                                                                                                                      
                                                                                                                                       
    for t in threads:                                                                                                                  
        t.join()                                                                                                                       
                                                                                                                                       
    print(f"\nFinal cache state: {cache.get('user:456')}")                                                                             
    print("Some updates might be lost due to read-modify-write races!")                                                            
                                                                                                                                       
                                                                                                                                       
if __name__ == "__main__":                                                                                                             
    print("\nCACHE INCONSISTENCY DEMO: Concurrent Writes\n")                                                                        
                                                                                                                                       
    scenario_1_race_condition()                                                                                                        
                                                                                                                                       
    time.sleep(1)  # Pause between scenarios                                                                                           
                                                                                                                                       
    scenario_2_interleaved_updates()                                                                                                   
                                                                                                                                       
    print("\n" + "=" * 70)                                                                                                             
    print("Key Takeaways:")                                                                                                            
    print("- Concurrent writes can cause last-write-wins issues")                                                                      
    print("- Cache updates aren't atomic with DB writes")                                                                              
    print("- Read-modify-write patterns are prone to lost updates")                                                                    
    print("=" * 70)