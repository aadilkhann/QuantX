"""
State persistence for LiveExecutionEngine.

Provides durable state storage to survive crashes and enable disaster recovery.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class EngineState:
    """Snapshot of engine state."""
    
    timestamp: datetime
    state: str  # EngineState enum value
    strategy_name: str
    broker_name: str
    positions: Dict[str, Any]
    pending_orders: List[str]
    statistics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngineState':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class StateStore:
    """
    Persistent state storage using SQLite.
    
    Stores engine state snapshots for crash recovery and audit trail.
    """
    
    def __init__(self, db_path: str = "data/quantx_state.db"):
        """
        Initialize state store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logger.info(f"StateStore initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Engine state snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS engine_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    state TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    broker_name TEXT NOT NULL,
                    positions TEXT NOT NULL,
                    pending_orders TEXT NOT NULL,
                    statistics TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Crash detection
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crash_markers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    engine_state_id INTEGER,
                    recovered BOOLEAN DEFAULT 0,
                    recovery_timestamp TEXT,
                    FOREIGN KEY (engine_state_id) REFERENCES engine_states(id)
                )
            """)
            
            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_states_timestamp 
                ON engine_states(timestamp DESC)
            """)
            
            conn.commit()
    
    def save_state(self, state: EngineState) -> int:
        """
        Save engine state snapshot.
        
        Args:
            state: Engine state to save
            
        Returns:
            State ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO engine_states 
                (timestamp, state, strategy_name, broker_name, positions, 
                 pending_orders, statistics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.timestamp.isoformat(),
                state.state,
                state.strategy_name,
                state.broker_name,
                json.dumps(state.positions),
                json.dumps(state.pending_orders),
                json.dumps(state.statistics),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            state_id = cursor.lastrowid
            
            logger.debug(f"Saved engine state {state_id} at {state.timestamp}")
            return state_id
    
    def get_latest_state(self) -> Optional[EngineState]:
        """
        Get most recent engine state.
        
        Returns:
            Latest engine state or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, state, strategy_name, broker_name, 
                       positions, pending_orders, statistics
                FROM engine_states
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return EngineState(
                timestamp=datetime.fromisoformat(row[0]),
                state=row[1],
                strategy_name=row[2],
                broker_name=row[3],
                positions=json.loads(row[4]),
                pending_orders=json.loads(row[5]),
                statistics=json.loads(row[6])
            )
    
    def mark_crash(self, state_id: Optional[int] = None) -> int:
        """
        Mark a crash event.
        
        Args:
            state_id: Optional state ID at crash time
            
        Returns:
            Crash marker ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO crash_markers (timestamp, engine_state_id)
                VALUES (?, ?)
            """, (datetime.now().isoformat(), state_id))
            
            conn.commit()
            crash_id = cursor.lastrowid
            
            logger.warning(f"Crash marker {crash_id} created")
            return crash_id
    
    def has_unrecovered_crash(self) -> bool:
        """
        Check if there's an unrecovered crash.
        
        Returns:
            True if unrecovered crash exists
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM crash_markers
                WHERE recovered = 0
            """)
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def mark_crash_recovered(self, crash_id: int):
        """
        Mark crash as recovered.
        
        Args:
            crash_id: Crash marker ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE crash_markers
                SET recovered = 1, recovery_timestamp = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), crash_id))
            
            conn.commit()
            logger.info(f"Crash {crash_id} marked as recovered")
    
    def get_state_history(self, limit: int = 100) -> List[EngineState]:
        """
        Get state history.
        
        Args:
            limit: Maximum number of states to return
            
        Returns:
            List of engine states
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, state, strategy_name, broker_name,
                       positions, pending_orders, statistics
                FROM engine_states
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            states = []
            for row in cursor.fetchall():
                states.append(EngineState(
                    timestamp=datetime.fromisoformat(row[0]),
                    state=row[1],
                    strategy_name=row[2],
                    broker_name=row[3],
                    positions=json.loads(row[4]),
                    pending_orders=json.loads(row[5]),
                    statistics=json.loads(row[6])
                ))
            
            return states
    
    def cleanup_old_states(self, days: int = 30):
        """
        Remove old state snapshots.
        
        Args:
            days: Remove states older than this many days
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM engine_states
                WHERE timestamp < ?
            """, (cutoff_iso,))
            
            deleted = cursor.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted} old state snapshots")
