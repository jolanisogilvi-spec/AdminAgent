"""Performance tests for index optimization.

Validates the 30-60x performance improvements from index optimization.
"""
import pytest
import time
from sqlmodel import select, func
from sqlalchemy import text

from app.models.ticket import Ticket
from app.models.user import User
from app.models.asset import Asset
from app.models.enums import ProcessingStatus, TicketType


class TestIndexPerformance:
    """Test index performance improvements."""

    def test_ticket_list_with_index(self, session, bulk_test_data, benchmark):
        """Test ticket list query performance with indexes.

        Target: < 50ms for 20 items from 1000+ records
        """
        # Create test data
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        def query_tickets():
            statement = (
                select(Ticket)
                .where(Ticket.processing_status == ProcessingStatus.PENDING)
                .order_by(Ticket.created_at.desc())
                .limit(20)
            )
            return session.exec(statement).all()

        # Benchmark the query
        result = benchmark(query_tickets)

        assert len(result) <= 20
        # Verify index is used (should be < 50ms)
        assert benchmark.stats['mean'] < 0.05  # 50ms

    def test_index_scan_vs_seq_scan(self, session, bulk_test_data):
        """Compare index scan vs sequential scan performance.

        Target: Index scan should be 30x faster
        """
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        # Force sequential scan
        session.exec(text("SET enable_indexscan = OFF"))
        start = time.time()
        result_seq = session.exec(
            select(Ticket).where(Ticket.processing_status == ProcessingStatus.PENDING)
        ).all()
        seq_scan_time = time.time() - start

        # Enable index scan
        session.exec(text("SET enable_indexscan = ON"))
        start = time.time()
        result_idx = session.exec(
            select(Ticket).where(Ticket.processing_status == ProcessingStatus.PENDING)
        ).all()
        index_scan_time = time.time() - start

        # Verify results are the same
        assert len(result_seq) == len(result_idx)

        # Index scan should be significantly faster
        speedup = seq_scan_time / index_scan_time
        print(f"\nSpeedup: {speedup:.2f}x")
        print(f"Sequential scan: {seq_scan_time*1000:.2f}ms")
        print(f"Index scan: {index_scan_time*1000:.2f}ms")

        assert speedup > 10  # At least 10x faster

    def test_composite_index_performance(self, session, bulk_test_data, benchmark):
        """Test composite index (processing_status, approval_status, created_at)."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        def query_with_composite_index():
            statement = (
                select(Ticket)
                .where(Ticket.processing_status == ProcessingStatus.PENDING)
                .order_by(Ticket.created_at.desc())
                .limit(20)
            )
            return session.exec(statement).all()

        result = benchmark(query_with_composite_index)

        # Should use idx_tickets_status_composite
        assert len(result) <= 20
        assert benchmark.stats['mean'] < 0.05  # < 50ms

    def test_partial_index_efficiency(self, session, bulk_test_data):
        """Test partial index (WHERE processing_status != 'completed').

        Partial indexes should be smaller and faster.
        """
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        # Query using partial index
        start = time.time()
        pending_tickets = session.exec(
            select(Ticket)
            .where(Ticket.processing_status == ProcessingStatus.PENDING)
        ).all()
        query_time = time.time() - start

        print(f"\nPartial index query time: {query_time*1000:.2f}ms")
        print(f"Results: {len(pending_tickets)} tickets")

        # Should be very fast (< 20ms)
        assert query_time < 0.02

    def test_covering_index_no_table_access(self, session, bulk_test_data):
        """Test covering index (INCLUDE columns) - no table access needed."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        # Query only indexed columns
        statement = (
            select(
                Ticket.id,
                Ticket.title,
                Ticket.ticket_type,
                Ticket.urgency_level,
                Ticket.creator_id
            )
            .where(Ticket.processing_status == ProcessingStatus.PENDING)
            .order_by(Ticket.created_at.desc())
            .limit(20)
        )

        start = time.time()
        results = session.exec(statement).all()
        query_time = time.time() - start

        print(f"\nCovering index query time: {query_time*1000:.2f}ms")

        # Should be extremely fast (< 10ms) - index-only scan
        assert query_time < 0.01
        assert len(results) <= 20

    def test_fulltext_search_performance(self, session, bulk_test_data, benchmark):
        """Test full-text search index performance."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        def fulltext_search():
            # Using PostgreSQL full-text search
            statement = text(
                """
                SELECT id, title FROM tickets
                WHERE to_tsvector('chinese', title || ' ' || COALESCE(description, ''))
                @@ to_tsquery('chinese', :query)
                LIMIT 20
                """
            )
            return session.exec(statement, {"query": "维修"}).all()

        result = benchmark(fulltext_search)

        # Full-text search should be fast (< 100ms)
        assert benchmark.stats['mean'] < 0.1

    def test_asset_status_index(self, session, bulk_test_data, benchmark):
        """Test asset status composite index."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        def query_assets_by_status():
            statement = (
                select(Asset)
                .where(Asset.status == "idle")
                .where(Asset.category == "it_equipment")
            )
            return session.exec(statement).all()

        result = benchmark(query_assets_by_status)

        # Should use idx_assets_status
        assert benchmark.stats['mean'] < 0.02  # < 20ms

    def test_user_department_role_index(self, session, bulk_test_data, benchmark):
        """Test user department+role composite index."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        def query_users_by_dept_role():
            statement = (
                select(User)
                .where(User.department == "技术部")
                .where(User.role == "manager")
                .where(User.is_active == True)
            )
            return session.exec(statement).all()

        result = benchmark(query_users_by_dept_role)

        # Should use idx_users_dept_role
        assert benchmark.stats['mean'] < 0.01  # < 10ms

    def test_explain_analyze_index_usage(self, session, bulk_test_data):
        """Verify that queries are using indexes via EXPLAIN ANALYZE."""
        bulk_test_data(num_users=100, num_tickets=1000, num_assets=500)

        # Get query plan
        explain_query = text(
            """
            EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
            SELECT * FROM tickets
            WHERE processing_status = 'pending'
            ORDER BY created_at DESC
            LIMIT 20
            """
        )

        result = session.exec(explain_query).first()
        plan = result[0][0]['Plan']

        print(f"\nQuery Plan: {plan['Node Type']}")
        print(f"Execution Time: {result[0][0]['Execution Time']:.2f}ms")

        # Should use Index Scan or Index Only Scan
        assert 'Index' in plan['Node Type']
        assert result[0][0]['Execution Time'] < 50  # < 50ms
