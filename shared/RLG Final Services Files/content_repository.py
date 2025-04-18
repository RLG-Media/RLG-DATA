# content_repository.py

import logging
import sqlite3
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ContentRepository:
    """Class for managing content storage and retrieval from a database."""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        logger.info(f"Database connected: {db_path}")

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def create_content_table(self):
        """Create a table for storing content if it does not exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    tags TEXT,
                    features BLOB,
                    popularity INTEGER DEFAULT 0,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            logger.info("Content table created or already exists.")
        except Exception as e:
            logger.error(f"Error creating content table: {e}")
            raise

    def add_content(self, title: str, description: str, tags: List[str], features: bytes):
        """Add new content to the database."""
        try:
            tags_str = ','.join(tags)
            self.cursor.execute("""
                INSERT INTO content (title, description, tags, features)
                VALUES (?, ?, ?, ?)
            """, (title, description, tags_str, features))
            self.conn.commit()
            logger.info(f"Content added: {title}")
        except Exception as e:
            logger.error(f"Error adding content: {e}")
            raise

    def get_content_by_id(self, content_id: int) -> Dict[str, Any]:
        """Retrieve content details by content ID."""
        try:
            self.cursor.execute("SELECT * FROM content WHERE id = ?", (content_id,))
            row = self.cursor.fetchone()
            if row:
                content = {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "tags": row[3].split(',') if row[3] else [],
                    "features": row[4],
                    "popularity": row[5],
                    "added_date": row[6]
                }
                logger.info(f"Content retrieved by ID: {content_id}")
                return content
            else:
                return None
        except Exception as e:
            logger.error(f"Error retrieving content by ID: {e}")
            return None

    def get_all_content(self) -> List[Dict[str, Any]]:
        """Retrieve all content from the database."""
        try:
            self.cursor.execute("SELECT * FROM content")
            rows = self.cursor.fetchall()
            content_list = [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "tags": row[3].split(',') if row[3] else [],
                    "features": row[4],
                    "popularity": row[5],
                    "added_date": row[6]
                }
                for row in rows
            ]
            logger.info(f"Retrieved all content, total: {len(content_list)}")
            return content_list
        except Exception as e:
            logger.error(f"Error retrieving all content: {e}")
            return []

    def search_content_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Search for content based on tags."""
        try:
            tags_str = ','.join(tags)
            self.cursor.execute("""
                SELECT * FROM content WHERE tags LIKE ?
            """, ('%' + tags_str + '%',))
            rows = self.cursor.fetchall()
            search_results = [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "tags": row[3].split(',') if row[3] else [],
                    "features": row[4],
                    "popularity": row[5],
                    "added_date": row[6]
                }
                for row in rows
            ]
            logger.info(f"Search content by tags: {tags_str}, results: {len(search_results)}")
            return search_results
        except Exception as e:
            logger.error(f"Error searching content by tags: {e}")
            return []

    def update_content_popularity(self, content_id: int, popularity_score: int):
        """Update the popularity score of a specific content item."""
        try:
            self.cursor.execute("""
                UPDATE content SET popularity = ? WHERE id = ?
            """, (popularity_score, content_id))
            self.conn.commit()
            logger.info(f"Updated popularity for content ID: {content_id}")
        except Exception as e:
            logger.error(f"Error updating popularity for content ID {content_id}: {e}")
            raise

    def delete_content(self, content_id: int):
        """Delete content from the database based on content ID."""
        try:
            self.cursor.execute("DELETE FROM content WHERE id = ?", (content_id,))
            self.conn.commit()
            logger.info(f"Deleted content ID: {content_id}")
        except Exception as e:
            logger.error(f"Error deleting content ID {content_id}: {e}")
            raise

# Additional Recommendations:
# 1. Implement pagination for fetching large datasets.
# 2. Add indexing to the database to improve search speed for tags and content retrieval.
# 3. Implement soft deletion (mark content as deleted instead of physically deleting).
# 4. Implement versioning to track content changes over time.
# 5. Enable content updates to handle modifications to existing content.
# 6. Introduce a content archiving system to keep historical content.
# 7. Implement proper database schema optimization for scalability.
# 8. Use caching mechanisms to improve read performance.
# 9. Add full-text search capabilities for searching content by title and description.
# 10. Secure database with user authentication and access controls.

