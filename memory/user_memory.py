import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class UserMemory:
    """用户记忆管理"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "user_memory.db"
        self.db_path = str(db_path)
        self._init_tables()

    def _init_tables(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 用户偏好表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key)
            )
        """)

        # 会话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 旅行规划表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travel_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                destination TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                feedback TEXT,
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 收藏表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, item_type, item_id)
            )
        """)

        conn.commit()
        conn.close()

    def save_preference(self, user_id: str, key: str, value: Any):
        """保存用户偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, key, json.dumps(value, ensure_ascii=False)))

        conn.commit()
        conn.close()

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户所有偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT preference_key, preference_value FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )

        preferences = {}
        for row in cursor.fetchall():
            preferences[row[0]] = json.loads(row[1])

        conn.close()
        return preferences

    def save_conversation(self, user_id: str, message: str, response: str,
                          session_id: str = None):
        """保存对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversation_history (user_id, session_id, message, response)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_id, message, response))

        conn.commit()
        conn.close()

    def get_conversation_history(self, user_id: str, limit: int = 20, session_id: str = None) -> List[Dict]:
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if session_id:
            cursor.execute("""
                SELECT message, response, created_at
                FROM conversation_history
                WHERE user_id = ? AND session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, session_id, limit))
        else:
            cursor.execute("""
                SELECT message, response, created_at
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))

        history = []
        for row in reversed(cursor.fetchall()):
            history.append({
                "message": row[0],
                "response": row[1],
                "created_at": row[2]
            })

        conn.close()
        return history

    def save_travel_plan(self, user_id: str, destination: str, plan_data: Dict):
        """保存旅行规划"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO travel_plans (user_id, destination, plan_data)
            VALUES (?, ?, ?)
        """, (user_id, destination, json.dumps(plan_data, ensure_ascii=False)))

        conn.commit()
        conn.close()

    def get_travel_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户旅行规划"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, destination, plan_data, rating, created_at
            FROM travel_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))

        plans = []
        for row in cursor.fetchall():
            plans.append({
                "id": row[0],
                "destination": row[1],
                "plan_data": json.loads(row[2]),
                "rating": row[3],
                "created_at": row[4]
            })

        conn.close()
        return plans

    def add_favorite(self, user_id: str, item_type: str, item_id: str, item_data: Dict):
        """添加收藏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO favorites (user_id, item_type, item_id, item_data)
                VALUES (?, ?, ?, ?)
            """, (user_id, item_type, item_id, json.dumps(item_data, ensure_ascii=False)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_favorites(self, user_id: str, item_type: str = None) -> List[Dict]:
        """获取收藏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if item_type:
            cursor.execute("""
                SELECT item_type, item_id, item_data, created_at
                FROM favorites
                WHERE user_id = ? AND item_type = ?
                ORDER BY created_at DESC
            """, (user_id, item_type))
        else:
            cursor.execute("""
                SELECT item_type, item_id, item_data, created_at
                FROM favorites
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))

        favorites = []
        for row in cursor.fetchall():
            favorites.append({
                "type": row[0],
                "id": row[1],
                "data": json.loads(row[2]),
                "created_at": row[3]
            })

        conn.close()
        return favorites

    def delete_favorite(self, user_id: str, item_type: str, item_id: str) -> bool:
        """删除收藏"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM favorites
            WHERE user_id = ? AND item_type = ? AND item_id = ?
        """, (user_id, item_type, item_id))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
