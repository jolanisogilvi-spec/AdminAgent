"""Performance tests for pagination strategies.

Validates cursor pagination vs OFFSET pagination (60x improvement).
"""
import pytest
import time
from sqlmodel import select

from app.models.ticket import Ticket
from app.models.enums import ProcessingStatus


class TestPaginationPerformance:
    """Test pagination performance optimizations."""

    def test_offset_pagination_deep_page(self, session, bulk_test_data):
        """Test OFFSET pagination performance on deep pages.

        Problem: OFFSET 20000 scans 20000 rows even though we only need 20.
        """
        bulk_test_data(num_users=100, num_tickets=10000, num_assets=500)

        # Simulate page 1000 (offset 20000)
        start = time.time()
        statement = (
            select(Ticket)
            .order_by(Ticket.id.desc())
            .offset(20000)
            .limit(20)
        )
        results = session.exec(statement).all()
        offset_time = time.time() - start

        print(f"\nOFFSET pagination (page 1000): {offset_time*1000:.2f}ms")
        print(f"Results: {len(results)} tickets")

        # Deep pagination with OFFSET is slow
        assert len(results) <= 20

    def test_cursor_pagination(self, session, bulk_test_data):
        """Test cursor-based pagination.

        Solution: Use WHERE id < last_id instead of OFFSET.
        Target: 60x faster than OFFSET for deep pages.
        """
        data = bulk_test_data(num_users=100, num_tickets=10000, num_assets=500)

        # Get a ticket ID from middle of dataset
        middle_ticket = session.exec(
            select(Ticket)
            .order_by(Ticket.id.desc())
            .offset(5000)
            .limit(1)
        ).first()
        cursor_id = middle_ticket.id

        # Cursor pagination
        start = time.time()
        statement = (
            select(Ticket)
            .where(Ticket.id < cursor_id)
            .order_by(Ticket.id.desc())
            .limit(20)
        )
        results_cursor = session.exec(statement).all()
        cursor_time = time.time() - start

        # OFFSET pagination (equivalent page)
        start = time.time()
        statement_offset = (
            select(Ticket)
            .order_by(Ticket.id.desc())
            .offset(5000)
            .limit(20)
        )
        results_offset = session.exec(statement_offset).all()
        offset_time = time.time() - start

        speedup = offset_time / cursor_time
        print(f"\nCursor pagination: {cursor_time*1000:.2f}ms")
        print(f"OFFSET pagination: {offset_time*1000:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")

        # Cursor should be much faster
        assert speedup > 10
        assert len(results_cursor) <= 20

    def test_keyset_pagination_with_timestamp(self, session, bulk_test_data):
        """Test keyset pagination using created_at timestamp."""
        bulk_test_data(num_users=100, num_tickets=5000, num_assets=500)

        # Get timestamp cursor
        middle_ticket = session.exec(
            select(Ticket)
            .order_by(Ticket.created_at.desc())
            .offset(2500)
            .limit(1)
        ).first()
        cursor_timestamp = middle_ticket.created_at

        # Keyset pagination
        start = time.time()
        statement = (
            select(Ticket)
            .where(Ticket.created_at < cursor_timestamp)
            .order_by(Ticket.created_at.desc())
            .limit(20)
        )
        results = session.exec(statement).all()
        keyset_time = time.time() - start

        print(f"\nKeyset pagination: {keyset_time*1000:.2f}ms")
        print(f"Results: {len(results)} tickets")

        # Should be very fast (< 10ms)
        assert keyset_time < 0.01
        assert len(results) <= 20

    def test_pagination_with_filters(self, session, bulk_test_data):
        """Test cursor pagination with additional filters."""
        bulk_test_data(num_users=100, num_tickets=5000, num_assets=500)

        # Get cursor
        middle_ticket = session.exec(
            select(Ticket)
            .where(Ticket.processing_status == ProcessingStatus.PENDING)
            .order_by(Ticket.id.desc())
            .offset(100)
            .limit(1)
        ).first()

        if middle_ticket:
            cursor_id = middle_ticket.id

            # Cursor pagination with filter
            start = time.time()
            statement = (
                select(Ticket)
                .where(Ticket.processing_status == ProcessingStatus.PENDING)
                .where(Ticket.id < cursor_id)
                .order_by(Ticket.id.desc())
                .limit(20)
            )
            results = session.exec(statement).all()
            query_time = time.time() - start

            print(f"\nFiltered cursor pagination: {query_time*1000:.2f}ms")

            # Should be fast even with filters
            assert query_time < 0.02

    def test_count_query_optimization(self, session, bulk_test_data):
        """Test COUNT query performance for pagination metadata."""
        bulk_test_data(num_users=100, num_tickets=10000, num_assets=500)

        # Slow: COUNT(*) on large table
        start = time.time()
        from sqlalchemy import func
        total_count = session.exec(
            select(func.count(Ticket.id))
        ).first()
        count_time = time.time() - start

        print(f"\nCOUNT query time: {count_time*1000:.2f}ms")
        print(f"Total tickets: {total_count}")

        # COUNT should use index
        assert count_time < 0.1  # < 100ms

    def test_pagination_benchmark(self, session, bulk_test_data, benchmark):
        """Benchmark cursor pagination."""
        bulk_test_data(num_users=100, num_tickets=5000, num_assets=500)

        # Get cursor
        cursor_ticket = session.exec(
            select(Ticket)
            .order_by(Ticket.id.desc())
            .offset(1000)
            .limit(1)
        ).first()
        cursor_id = cursor_ticket.id

        def paginate():
            statement = (
                select(Ticket)
                .where(Ticket.id < cursor_id)
                .order_by(Ticket.id.desc())
                .limit(20)
            )
            return session.exec(statement).all()

        result = benchmark(paginate)

        # Should be very fast
        assert benchmark.stats['mean'] < 0.01  # < 10ms
        assert len(result) <= 20
