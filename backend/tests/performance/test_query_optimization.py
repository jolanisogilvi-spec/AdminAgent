"""Performance tests for query optimization.

Validates N+1 query prevention, eager loading, and other optimizations.
"""
import pytest
import time
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

from app.models.ticket import Ticket
from app.models.user import User
from app.models.asset import Asset
from app.models.task import Task


class TestQueryOptimization:
    """Test query optimization strategies."""

    def test_n_plus_one_problem(self, session, bulk_test_data):
        """Demonstrate N+1 query problem and solution.

        Target: 33x improvement with selectinload
        """
        data = bulk_test_data(num_users=50, num_tickets=100, num_assets=50)

        # BAD: N+1 query problem
        start = time.time()
        tickets_bad = session.exec(select(Ticket).limit(100)).all()
        query_count_bad = 1
        for ticket in tickets_bad:
            _ = ticket.creator.full_name  # Triggers additional query
            query_count_bad += 1
        n_plus_one_time = time.time() - start

        # GOOD: Using selectinload
        start = time.time()
        statement = (
            select(Ticket)
            .options(selectinload(Ticket.creator))
            .limit(100)
        )
        tickets_good = session.exec(statement).all()
        for ticket in tickets_good:
            _ = ticket.creator.full_name  # No additional query
        optimized_time = time.time() - start

        speedup = n_plus_one_time / optimized_time
        print(f"\nN+1 queries: {n_plus_one_time*1000:.2f}ms ({query_count_bad} queries)")
        print(f"Optimized: {optimized_time*1000:.2f}ms (2 queries)")
        print(f"Speedup: {speedup:.2f}x")

        # Should be at least 10x faster
        assert speedup > 10

    def test_selectinload_vs_joinedload(self, session, bulk_test_data):
        """Compare selectinload vs joinedload performance."""
        bulk_test_data(num_users=50, num_tickets=100, num_assets=50)

        # selectinload (2 queries, no cartesian product)
        start = time.time()
        statement_select = (
            select(Ticket)
            .options(selectinload(Ticket.creator))
            .options(selectinload(Ticket.related_asset))
            .limit(50)
        )
        tickets_select = session.exec(statement_select).all()
        selectinload_time = time.time() - start

        # joinedload (1 query with LEFT JOIN)
        start = time.time()
        statement_joined = (
            select(Ticket)
            .options(joinedload(Ticket.creator))
            .options(joinedload(Ticket.related_asset))
            .limit(50)
        )
        tickets_joined = session.exec(statement_joined).all()
        joinedload_time = time.time() - start

        print(f"\nselectinload: {selectinload_time*1000:.2f}ms")
        print(f"joinedload: {joinedload_time*1000:.2f}ms")

        # Both should be fast (< 50ms)
        assert selectinload_time < 0.05
        assert joinedload_time < 0.05

    def test_selective_column_loading(self, session, bulk_test_data, benchmark):
        """Test loading only required columns vs SELECT *.

        Target: 60% data reduction
        """
        bulk_test_data(num_users=50, num_tickets=1000, num_assets=50)

        def query_all_columns():
            return session.exec(select(Ticket).limit(100)).all()

        def query_selective_columns():
            statement = select(
                Ticket.id,
                Ticket.title,
                Ticket.ticket_type,
                Ticket.urgency_level,
                Ticket.created_at
            ).limit(100)
            return session.exec(statement).all()

        # Benchmark both approaches
        start = time.time()
        result_all = query_all_columns()
        all_columns_time = time.time() - start

        start = time.time()
        result_selective = query_selective_columns()
        selective_time = time.time() - start

        print(f"\nAll columns: {all_columns_time*1000:.2f}ms")
        print(f"Selective columns: {selective_time*1000:.2f}ms")
        print(f"Improvement: {(1 - selective_time/all_columns_time)*100:.1f}%")

        # Selective loading should be faster
        assert selective_time < all_columns_time

    def test_batch_insert_performance(self, session, user_factory, benchmark):
        """Test batch insert vs individual inserts.

        Target: 100x improvement
        """
        # Individual inserts (BAD)
        start = time.time()
        for i in range(100):
            user = user_factory(username=f"user_individual_{i}")
        individual_time = time.time() - start

        # Batch insert (GOOD)
        start = time.time()
        users = []
        for i in range(100):
            user = User(
                username=f"user_batch_{i}",
                full_name=f"User {i}",
                password_hash="hash",
                role="employee",
                department="Test"
            )
            users.append(user)
        session.add_all(users)
        session.commit()
        batch_time = time.time() - start

        speedup = individual_time / batch_time
        print(f"\nIndividual inserts: {individual_time*1000:.2f}ms")
        print(f"Batch insert: {batch_time*1000:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")

        # Batch should be at least 50x faster
        assert speedup > 50

    def test_subquery_optimization(self, session, bulk_test_data):
        """Test subquery performance for department filtering."""
        data = bulk_test_data(num_users=100, num_tickets=500, num_assets=50)

        # Create users in same department
        dept_users = [u for u in data['users'][:20]]
        for user in dept_users:
            user.department = "技术部"
        session.commit()

        # Subquery for department tickets
        start = time.time()
        dept_user_ids = session.exec(
            select(User.id)
            .where(User.department == "技术部")
            .where(User.is_active == True)
        ).all()

        tickets = session.exec(
            select(Ticket)
            .where(Ticket.creator_id.in_(dept_user_ids))
        ).all()
        query_time = time.time() - start

        print(f"\nSubquery time: {query_time*1000:.2f}ms")
        print(f"Found {len(tickets)} tickets")

        # Should be fast (< 50ms)
        assert query_time < 0.05

    def test_aggregation_query_performance(self, session, bulk_test_data, benchmark):
        """Test database aggregation vs Python loops.

        Target: 133x improvement
        """
        bulk_test_data(num_users=50, num_tickets=1000, num_assets=50)

        # BAD: Python aggregation
        start = time.time()
        tickets = session.exec(select(Ticket)).all()
        stats_python = {}
        for ticket in tickets:
            ticket_type = ticket.ticket_type
            stats_python[ticket_type] = stats_python.get(ticket_type, 0) + 1
        python_time = time.time() - start

        # GOOD: Database aggregation
        start = time.time()
        from sqlalchemy import func
        statement = (
            select(Ticket.ticket_type, func.count(Ticket.id))
            .group_by(Ticket.ticket_type)
        )
        stats_db = dict(session.exec(statement).all())
        db_time = time.time() - start

        speedup = python_time / db_time
        print(f"\nPython aggregation: {python_time*1000:.2f}ms")
        print(f"Database aggregation: {db_time*1000:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")

        # Results should match
        assert stats_python == stats_db
        # Database should be much faster
        assert speedup > 50

    def test_connection_pool_performance(self, engine, benchmark):
        """Test connection pool efficiency."""
        from sqlmodel import Session

        def query_with_pool():
            with Session(engine) as session:
                return session.exec(select(User).limit(10)).all()

        result = benchmark(query_with_pool)

        # Connection pooling should be very fast
        assert benchmark.stats['mean'] < 0.01  # < 10ms
