"""
Measuring Cache Staleness Impact

This example demonstrates how to quantify staleness in a cache by comparing
cached values against the "true" database state during concurrent updates.
"""

import threading
import time
import random
from typing import Any, Dict, Optional
from simple_cache import SimpleCache


class DatabaseSimulator:
    """Simulates a database with direct read/write access."""

    def __init__(self):
        self._db: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def write(self, key: str, value: Any, delay: float = 0.01) -> None:
        """Write to database with simulated I/O delay."""
        time.sleep(delay)
        with self._lock:
            self._db[key] = value

    def read(self, key: str) -> Optional[Any]:
        """Read directly from database (bypasses cache)."""
        with self._lock:
            return self._db.get(key)

    def set_initial(self, key: str, value: Any) -> None:
        """Set initial value without delay."""
        with self._lock:
            self._db[key] = value


def writer_thread(
    db: DatabaseSimulator,
    cache: SimpleCache,
    key: str,
    num_updates: int,
    write_delay: float,
    cache_update_delay: float = 0.005
) -> None:
    """
    Continuously update database and cache.

    Simulates write-through pattern: DB write -> cache update
    The gap between these operations is where staleness occurs!

    Args:
        cache_update_delay: Simulates network latency or async propagation delay
                           between DB write and cache update (default 5ms)
    """
    for i in range(num_updates):
        new_value = f"version_{i}"

        # Step 1: Write to database (slow)
        db.write(key, new_value, delay=write_delay)

        # Simulate propagation delay (network latency, async updates, etc.)
        time.sleep(cache_update_delay)

        # Step 2: Update cache
        cache.set(key, new_value)

        # Small random delay between updates
        time.sleep(random.uniform(0.001, 0.005))


def measure_staleness_basic():
    """
    Basic staleness measurement: Single writer, multiple readers.

    Shows how often readers see stale data during concurrent updates.
    """
    print("\n" + "=" * 70)
    print("BASIC STALENESS MEASUREMENT")
    print("=" * 70)

    db = DatabaseSimulator()
    cache = SimpleCache(default_ttl=10.0)

    # Initial state
    key = "user:1:profile"
    initial_value = "version_0"
    db.set_initial(key, initial_value)
    cache.set(key, initial_value)

    print(f"Initial state: {initial_value}")
    print(f"Simulating 5ms cache propagation delay...")
    print(f"Running 1000 reads while writer updates concurrently...\n")

    # Start writer thread
    num_updates = 100
    writer = threading.Thread(
        target=writer_thread,
        args=(db, cache, key, num_updates, 0.01),
        daemon=True
    )
    writer.start()

    # Perform reads and measure staleness
    stale_count = 0
    total_reads = 1000

    for _ in range(total_reads):
        # Read from cache
        cached_val = cache.get(key)

        # Read true value from database (bypass cache)
        true_val = db.read(key)

        # Check if stale
        if cached_val != true_val:
            stale_count += 1

        # Small delay between reads
        time.sleep(0.001)

    writer.join()

    staleness_ratio = stale_count / total_reads
    print(f"Total reads: {total_reads}")
    print(f"Stale reads: {stale_count}")
    print(f"Staleness Ratio: {staleness_ratio:.2%}")
    print(f"Cache hit accuracy: {(1 - staleness_ratio):.2%}")
    if stale_count > 0:
        print(f"Cache served stale data {stale_count} times during concurrent updates!")


def measure_staleness_with_varying_delays():
    """
    Advanced measurement: Test staleness under different cache propagation delays.

    Shows how cache update latency affects staleness probability.
    """
    print("\n" + "=" * 70)
    print("STALENESS vs CACHE PROPAGATION DELAY")
    print("=" * 70)

    cache_propagation_delays = [0.001, 0.005, 0.01, 0.02, 0.05]

    print(f"{'Propagation Delay':<20} {'Staleness Ratio':<20} {'Stale Reads'}")
    print("-" * 70)

    for cache_delay in cache_propagation_delays:
        db = DatabaseSimulator()
        cache = SimpleCache(default_ttl=10.0)

        key = "user:test"
        db.set_initial(key, "v0")
        cache.set(key, "v0")

        # Start writer with varying cache propagation delay
        writer = threading.Thread(
            target=writer_thread,
            args=(db, cache, key, 50, 0.01, cache_delay),
            daemon=True
        )
        writer.start()

        # Measure staleness
        stale_count = 0
        total_reads = 500

        for _ in range(total_reads):
            cached_val = cache.get(key)
            true_val = db.read(key)

            if cached_val != true_val:
                stale_count += 1

            time.sleep(0.001)

        writer.join()

        staleness_ratio = stale_count / total_reads
        print(f"{cache_delay * 1000:>8.1f}ms           {staleness_ratio:>6.2%}               {stale_count}/{total_reads}")


def measure_staleness_multiple_writers():
    """
    Multiple writers scenario: Highest chance of staleness.

    Multiple threads updating the same key creates race conditions.
    """
    print("\n" + "=" * 70)
    print("STALENESS WITH MULTIPLE WRITERS")
    print("=" * 70)

    db = DatabaseSimulator()
    cache = SimpleCache(default_ttl=10.0)

    key = "counter"
    db.set_initial(key, 0)
    cache.set(key, 0)

    num_writers = 3
    cache_propagation_delay = 0.01  # 10ms delay
    print(f"Spawning {num_writers} concurrent writers...")
    print(f"Cache propagation delay: {cache_propagation_delay * 1000}ms")
    print(f"Measuring staleness over 1000 reads...\n")

    # Start multiple writers
    writers = []
    for i in range(num_writers):
        writer = threading.Thread(
            target=writer_thread,
            args=(db, cache, key, 50, 0.01, cache_propagation_delay),
            daemon=True
        )
        writers.append(writer)
        writer.start()

    # Measure staleness
    stale_count = 0
    total_reads = 1000

    for _ in range(total_reads):
        cached_val = cache.get(key)
        true_val = db.read(key)

        if cached_val != true_val:
            stale_count += 1

        time.sleep(0.001)

    for writer in writers:
        writer.join()

    staleness_ratio = stale_count / total_reads
    print(f"Total reads: {total_reads}")
    print(f"Stale reads: {stale_count}")
    print(f"Staleness Ratio: {staleness_ratio:.2%}")
    print("Multiple writers significantly increase staleness!")


if __name__ == "__main__":
    print("\nCACHE STALENESS MEASUREMENT DEMO\n")

    measure_staleness_basic()

    time.sleep(0.5)

    measure_staleness_with_varying_delays()

    time.sleep(0.5)

    measure_staleness_multiple_writers()

    print("\n" + "=" * 70)
    print("Key Insights:")
    print("- Staleness occurs in the gap between DB write and cache update")
    print("- Higher write latency = higher staleness probability")
    print("- Multiple writers amplify the problem")
    print("- Even small delays can cause significant stale reads")
    print("=" * 70)
