import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings


class UserMemory:
    """用户记忆管理"""

    def __init__(self):
        self.db_type = settings.DATABASE_TYPE
        if self.db_type == "mysql":
            self._init_mysql()
        else:
            self._init_sqlite()

    def _get_connection(self):
        """获取数据库连接"""
        if self.db_type == "mysql":
            import pymysql
            return pymysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            import sqlite3
            return sqlite3.connect(settings.DATABASE_PATH)

    def _init_sqlite(self):
        """初始化SQLite数据库"""
        import sqlite3
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _init_mysql(self):
        """初始化MySQL数据库"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                preference_key VARCHAR(255) NOT NULL,
                preference_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_pref (user_id, preference_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_id VARCHAR(255),
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_session (user_id, session_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travel_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                plan_data TEXT NOT NULL,
                feedback TEXT,
                rating INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                item_type VARCHAR(50) NOT NULL,
                item_id VARCHAR(255) NOT NULL,
                item_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_favorite (user_id, item_type, item_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                nickname VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        conn.close()

    def _placeholder(self):
        """返回数据库占位符"""
        return "%s" if self.db_type == "mysql" else "?"

    def register_user(self, username: str, password: str, nickname: str = None) -> Optional[Dict]:
        """注册用户"""
        conn = self._get_connection()
        p = self._placeholder()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            sql = f"""
                INSERT INTO users (username, password_hash, nickname)
                VALUES ({p}, {p}, {p})
            """
            cursor = self._execute(conn, sql, (username, password_hash, nickname or username))
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username, "nickname": nickname or username}
        except Exception:
            return None
        finally:
            conn.close()

    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """登录验证"""
        conn = self._get_connection()
        p = self._placeholder()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        sql = f"""
            SELECT id, username, nickname, created_at
            FROM users
            WHERE username = {p} AND password_hash = {p}
        """
        cursor = self._execute(conn, sql, (username, password_hash))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        if self.db_type == "mysql":
            return {"id": row["id"], "username": row["username"], "nickname": row["nickname"], "created_at": row["created_at"]}
        else:
            return {"id": row[0], "username": row[1], "nickname": row[2], "created_at": row[3]}

    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        conn = self._get_connection()
        p = self._placeholder()

        sql = f"""
            SELECT id, username, nickname, created_at
            FROM users
            WHERE id = {p}
        """
        cursor = self._execute(conn, sql, (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        if self.db_type == "mysql":
            return {"id": row["id"], "username": row["username"], "nickname": row["nickname"], "created_at": row["created_at"]}
        else:
            return {"id": row[0], "username": row[1], "nickname": row[2], "created_at": row[3]}

    def _execute(self, conn, sql, params=None):
        """执行SQL语句"""
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor

    def save_preference(self, user_id: str, key: str, value: Any):
        """保存用户偏好"""
        conn = self._get_connection()
        p = self._placeholder()

        if self.db_type == "mysql":
            sql = f"""
                INSERT INTO user_preferences (user_id, preference_key, preference_value, updated_at)
                VALUES ({p}, {p}, {p}, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE preference_value={p}, updated_at=CURRENT_TIMESTAMP
            """
            self._execute(conn, sql, (user_id, key, json.dumps(value, ensure_ascii=False), json.dumps(value, ensure_ascii=False)))
        else:
            sql = f"""
                INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value, updated_at)
                VALUES ({p}, {p}, {p}, CURRENT_TIMESTAMP)
            """
            self._execute(conn, sql, (user_id, key, json.dumps(value, ensure_ascii=False)))

        conn.commit()
        conn.close()

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户所有偏好"""
        conn = self._get_connection()
        p = self._placeholder()

        cursor = self._execute(conn, f"SELECT preference_key, preference_value FROM user_preferences WHERE user_id = {p}", (user_id,))

        preferences = {}
        for row in cursor.fetchall():
            if self.db_type == "mysql":
                preferences[row["preference_key"]] = json.loads(row["preference_value"])
            else:
                preferences[row[0]] = json.loads(row[1])

        conn.close()
        return preferences

    def save_conversation(self, user_id: str, message: str, response: str,
                          session_id: str = None):
        """保存对话历史"""
        conn = self._get_connection()
        p = self._placeholder()

        sql = f"""
            INSERT INTO conversation_history (user_id, session_id, message, response)
            VALUES ({p}, {p}, {p}, {p})
        """
        self._execute(conn, sql, (user_id, session_id, message, response))

        conn.commit()
        conn.close()

    def get_conversation_history(self, user_id: str, limit: int = 20, session_id: str = None) -> List[Dict]:
        """获取对话历史"""
        conn = self._get_connection()
        p = self._placeholder()

        if session_id:
            sql = f"""
                SELECT message, response, created_at
                FROM conversation_history
                WHERE user_id = {p} AND session_id = {p}
                ORDER BY created_at DESC
                LIMIT {p}
            """
            cursor = self._execute(conn, sql, (user_id, session_id, limit))
        else:
            sql = f"""
                SELECT message, response, created_at
                FROM conversation_history
                WHERE user_id = {p}
                ORDER BY created_at DESC
                LIMIT {p}
            """
            cursor = self._execute(conn, sql, (user_id, limit))

        history = []
        for row in reversed(cursor.fetchall()):
            if self.db_type == "mysql":
                history.append({
                    "message": row["message"],
                    "response": row["response"],
                    "created_at": row["created_at"]
                })
            else:
                history.append({
                    "message": row[0],
                    "response": row[1],
                    "created_at": row[2]
                })

        conn.close()
        return history

    def save_travel_plan(self, user_id: str, destination: str, plan_data: Dict):
        """保存旅行规划"""
        conn = self._get_connection()
        p = self._placeholder()

        sql = f"""
            INSERT INTO travel_plans (user_id, destination, plan_data)
            VALUES ({p}, {p}, {p})
        """
        self._execute(conn, sql, (user_id, destination, json.dumps(plan_data, ensure_ascii=False)))

        conn.commit()
        conn.close()

    def get_travel_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户旅行规划"""
        conn = self._get_connection()
        p = self._placeholder()

        sql = f"""
            SELECT id, destination, plan_data, rating, created_at
            FROM travel_plans
            WHERE user_id = {p}
            ORDER BY created_at DESC
            LIMIT {p}
        """
        cursor = self._execute(conn, sql, (user_id, limit))

        plans = []
        for row in cursor.fetchall():
            if self.db_type == "mysql":
                plans.append({
                    "id": row["id"],
                    "destination": row["destination"],
                    "plan_data": json.loads(row["plan_data"]),
                    "rating": row["rating"],
                    "created_at": row["created_at"]
                })
            else:
                plans.append({
                    "id": row[0],
                    "destination": row[1],
                    "plan_data": json.loads(row[2]),
                    "rating": row[3],
                    "created_at": row[4]
                })

        conn.close()
        return plans

    def add_favorite(self, user_id: str, item_type: str, item_id: str, item_data: Dict) -> bool:
        """添加收藏"""
        conn = self._get_connection()
        p = self._placeholder()

        try:
            sql = f"""
                INSERT INTO favorites (user_id, item_type, item_id, item_data)
                VALUES ({p}, {p}, {p}, {p})
            """
            self._execute(conn, sql, (user_id, item_type, item_id, json.dumps(item_data, ensure_ascii=False)))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_favorites(self, user_id: str, item_type: str = None) -> List[Dict]:
        """获取收藏"""
        conn = self._get_connection()
        p = self._placeholder()

        if item_type:
            sql = f"""
                SELECT item_type, item_id, item_data, created_at
                FROM favorites
                WHERE user_id = {p} AND item_type = {p}
                ORDER BY created_at DESC
            """
            cursor = self._execute(conn, sql, (user_id, item_type))
        else:
            sql = f"""
                SELECT item_type, item_id, item_data, created_at
                FROM favorites
                WHERE user_id = {p}
                ORDER BY created_at DESC
            """
            cursor = self._execute(conn, sql, (user_id,))

        favorites = []
        for row in cursor.fetchall():
            if self.db_type == "mysql":
                favorites.append({
                    "type": row["item_type"],
                    "id": row["item_id"],
                    "data": json.loads(row["item_data"]),
                    "created_at": row["created_at"]
                })
            else:
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
        conn = self._get_connection()
        p = self._placeholder()

        sql = f"""
            DELETE FROM favorites
            WHERE user_id = {p} AND item_type = {p} AND item_id = {p}
        """
        cursor = self._execute(conn, sql, (user_id, item_type, item_id))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
