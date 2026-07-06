"""数据库迁移工具 — 为 SQLite 安全添加新列和表"""
import sqlite3
import os


def get_db_path():
    """获取数据库文件路径"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "rental.db")


def column_exists(db_path: str, table: str, column: str) -> bool:
    """检查表中是否已存在某列"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return column in columns


def table_exists(db_path: str, table: str) -> bool:
    """检查表是否存在"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def add_column(db_path: str, table: str, column: str, col_type: str):
    """安全添加列（如果不存在）"""
    conn = sqlite3.connect(db_path)
    if not column_exists(db_path, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"  [OK] Added {table}.{column} ({col_type})")
    else:
        print(f"  [SKIP] {table}.{column} already exists")
    conn.commit()
    conn.close()


def create_table_if_not_exists(db_path: str, table: str, ddl: str):
    """安全创建表（如果不存在）"""
    conn = sqlite3.connect(db_path)
    if not table_exists(db_path, table):
        conn.execute(ddl)
        print(f"  [OK] Created table {table}")
    else:
        print(f"  [SKIP] Table {table} already exists")
    conn.commit()
    conn.close()


def run_migrations():
    """执行所有数据库迁移"""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print("[WARN] Database file not found, skipping migrations (ORM will create)")
        return

    print("[INFO] Starting database migrations...")

    # 1. houses 表新增列
    add_column(db_path, "houses", "latitude", "FLOAT")
    add_column(db_path, "houses", "longitude", "FLOAT")
    add_column(db_path, "houses", "commute_duration", "INTEGER")
    add_column(db_path, "houses", "commute_score", "FLOAT")

    # 2. 创建 districts 表
    create_table_if_not_exists(db_path, "districts", """
        CREATE TABLE districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(20) NOT NULL UNIQUE,
            center_lat FLOAT NOT NULL DEFAULT 0.0,
            center_lng FLOAT NOT NULL DEFAULT 0.0,
            pinyin VARCHAR(50),
            house_count INTEGER DEFAULT 0
        )
    """)

    # 3. 创建 workspace_configs 表
    create_table_if_not_exists(db_path, "workspace_configs", """
        CREATE TABLE workspace_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workplace_name VARCHAR(200),
            workplace_lat FLOAT NOT NULL,
            workplace_lng FLOAT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. 创建 favorites 表
    create_table_if_not_exists(db_path, "favorites", """
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER NOT NULL REFERENCES houses(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)

    print("[OK] Database migrations complete")


if __name__ == "__main__":
    run_migrations()
