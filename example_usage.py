"""Example usage for Dynamic Connection Pool & Leak Sentinel."""
from client import DynamicConnectionPoolSentinel

if __name__ == "__main__":
    res = DynamicConnectionPoolSentinel.acquire_connection("worker-agent-1", active_count=9, max_pool_size=10)
    print("Acquisition:", res)

    leaks = DynamicConnectionPoolSentinel.detect_leaks([
        {"lease_id": "lease_1", "client_label": "agent_alpha", "last_heartbeat": 100.0}
    ], max_idle_seconds=30.0, current_time=150.0)
    print("Leak Audit:", leaks)
