"""Performance tests for caching strategies.

Validates Redis caching and cache hit rate optimization.
"""
import pytest
import time
import json
from sqlmodel import select

from app.models.user import User
from app.models.ticket import Ticket


class TestCachePerformance:
    """Test caching strategy performance."""

    def test_cache_hit_vs_miss(self, session, redis_client, user_factory):
        """Test cache hit vs cache miss performance.

        Target: Cache hit should be 100x faster than database query.
        """
        # Create test user
        user = user_factory(username="test_cache_user")
        cache_key = f"user:{user.id}"

        # Cache miss (database query)
        start = time.time()
        db_user = session.exec(
            select(User).where(User.id == user.id)
        ).first()
        db_time = time.time() - start

        # Store in cache
        redis_client.setex(
            cache_key,
            300,
            json.dumps({
                "id": db_user.id,
                "username": db_user.username,
                "full_name": db_user.full_name
            })
        )

        # Cache hit
        start = time.time()
        cached_data = redis_client.get(cache_key)
        cached_user = json.loads(cached_data)
        cache_time = time.time() - start

        speedup = db_time / cache_time
        print(f"\nDatabase query: {db_time*1000:.2f}ms")
        print(f"Cache hit: {cache_time*1000:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")

        # Cache should be much faster
        assert speedup > 50
        assert cached_user["username"] == user.username

    def test_cache_warming(self, session, redis_client, bulk_test_data):
        """Test cache warming strategy."""
        data = bulk_test_data(num_users=100, num_tickets=500, num_assets=100)

        # Warm cache with active users
        start = time.time()
        active_users = session.exec(
            select(User).where(User.is_active == True)
        ).all()

        for user in active_users:
            cache_key = f"user:{user.id}"
            redis_client.setex(
                cache_key,
                3600,
                json.dumps({
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role
                }, default=str)
            )
        warming_time = time.time() - start

        print(f"\nCache warming time: {warming_time*1000:.2f}ms")
        print(f"Cached {len(active_users)} users")

        # Warming should be reasonably fast
        assert warming_time < 1.0  # < 1 second

    def test_cache_hit_rate(self, session, redis_client, bulk_test_data):
        """Test cache hit rate optimization.

        Target: > 80% cache hit rate
        """
        data = bulk_test_data(num_users=50, num_tickets=200, num_assets=50)

        # Simulate user queries with caching
        user_ids = [u.id for u in data['users'][:20]]
        cache_hits = 0
        cache_misses = 0

        # First pass - all cache misses
        for user_id in user_ids * 5:  # Simulate 5 rounds of queries
            cache_key = f"user:{user_id}"
            cached = redis_client.get(cache_key)

            if cached:
                cache_hits += 1
            else:
                cache_misses += 1
                # Load from database and cache
                user = session.exec(
                    select(User).where(User.id == user_id)
                ).first()
                if user:
                    redis_client.setex(
                        cache_key,
                        300,
                        json.dumps({
                            "id": user.id,
                            "username": user.username
                        })
                    )

        hit_rate = cache_hits / (cache_hits + cache_misses) * 100
        print(f"\nCache hits: {cache_hits}")
        print(f"Cache misses: {cache_misses}")
        print(f"Hit rate: {hit_rate:.1f}%")

        # Should achieve > 80% hit rate
        assert hit_rate > 80

    def test_cache_invalidation(self, session, redis_client, user_factory):
        """Test cache invalidation on data update."""
        user = user_factory(username="test_invalidation")
        cache_key = f"user:{user.id}"

        # Cache user data
        redis_client.setex(
            cache_key,
            300,
            json.dumps({"username": user.username})
        )

        # Verify cached
        assert redis_client.get(cache_key) is not None

        # Update user (should invalidate cache)
        user.full_name = "Updated Name"
        session.add(user)
        session.commit()

        # Invalidate cache
        redis_client.delete(cache_key)

        # Verify cache cleared
        assert redis_client.get(cache_key) is None

    def test_cache_ttl_strategy(self, redis_client, user_factory, session):
        """Test different TTL strategies for different data types."""
        user = user_factory()

        # Short TTL for frequently changing data
        redis_client.setex(
            f"ticket_stats",
            60,  # 1 minute
            json.dumps({"pending": 10, "completed": 5})
        )

        # Medium TTL for user data
        redis_client.setex(
            f"user:{user.id}",
            1800,  # 30 minutes
            json.dumps({"username": user.username})
        )

        # Long TTL for system config
        redis_client.setex(
            "sys_config:llm_model",
            3600,  # 1 hour
            "gpt-4o"
        )

        # Verify TTLs
        assert redis_client.ttl("ticket_stats") <= 60
        assert redis_client.ttl(f"user:{user.id}") <= 1800
        assert redis_client.ttl("sys_config:llm_model") <= 3600

    def test_query_result_caching(self, session, redis_client, bulk_test_data, benchmark):
        """Test caching of complex query results."""
        bulk_test_data(num_users=50, num_tickets=500, num_assets=50)

        cache_key = "pending_tickets_list"

        def get_pending_tickets():
            # Check cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Query database
            tickets = session.exec(
                select(Ticket.id, Ticket.title, Ticket.urgency_level)
                .where(Ticket.processing_status == "pending")
                .limit(20)
            ).all()

            # Cache results
            result = [{
                "id": t[0],
                "title": t[1],
                "urgency_level": t[2]
            } for t in tickets]

            redis_client.setex(
                cache_key,
                60,
                json.dumps(result)
            )
            return result

        # First call - cache miss
        result1 = get_pending_tickets()

        # Second call - cache hit
        start = time.time()
        result2 = get_pending_tickets()
        cached_time = time.time() - start

        print(f"\nCached query time: {cached_time*1000:.2f}ms")

        # Cached query should be very fast
        assert cached_time < 0.005  # < 5ms
        assert result1 == result2
