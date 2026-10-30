"""Dynamic Connection Pool & Leak Sentinel.
100% Python Standard Library.
"""

import time

class DynamicConnectionPoolSentinel:
    """Monitors connection acquisition timeouts, detects unclosed leaks, and dynamically resizes pools."""

    @staticmethod
    def acquire_connection(client_label: str, active_count: int, max_pool_size: int = 10,
                           burst_limit: int = 15, dynamic_expand: bool = True) -> dict:
        timestamp = time.time()
        if active_count < max_pool_size:
            return {
                "status": "ACQUIRED",
                "pool_tier": "STANDARD",
                "current_active": active_count + 1,
                "lease_id": f"lease_{client_label}_{int(timestamp * 1000)}",
                "acquired_at": timestamp
            }
        elif dynamic_expand and active_count < burst_limit:
            return {
                "status": "ACQUIRED",
                "pool_tier": "BURST_EXPANDED",
                "current_active": active_count + 1,
                "lease_id": f"burst_lease_{client_label}_{int(timestamp * 1000)}",
                "acquired_at": timestamp,
                "warning": "Pool operated in burst expansion mode"
            }
        else:
            return {
                "status": "EXHAUSTED",
                "pool_tier": "SATURATED",
                "current_active": active_count,
                "error": "Connection pool limit reached and burst cap exceeded",
                "recommended_action": "QUEUE_REQUEST_OR_SHED_LOAD"
            }

    @staticmethod
    def detect_leaks(active_leases: list, max_idle_seconds: float = 30.0, current_time: float = None) -> dict:
        now = current_time if current_time is not None else time.time()
        leaked_leases = []
        healthy_leases = []

        for lease in active_leases:
            acquired = lease.get("acquired_at", now)
            last_hb = lease.get("last_heartbeat", acquired)
            idle_duration = now - last_hb
            if idle_duration > max_idle_seconds:
                leaked_leases.append({
                    "lease_id": lease.get("lease_id"),
                    "client_label": lease.get("client_label"),
                    "idle_seconds": round(idle_duration, 2),
                    "action": "FORCE_RECLAIM_RECOMMENDED"
                })
            else:
                healthy_leases.append(lease.get("lease_id"))

        health_score = 100.0 if not active_leases else round((len(healthy_leases) / len(active_leases)) * 100.0, 1)

        return {
            "total_active_checked": len(active_leases),
            "leaks_detected_count": len(leaked_leases),
            "leaked_leases": leaked_leases,
            "pool_health_score": health_score,
            "status": "HEALTHY" if not leaked_leases else "LEAK_WARNING"
        }
