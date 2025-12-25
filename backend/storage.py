# backend/storage.py
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import settings

class DataStorage:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Sessions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_path TEXT,
                parquet_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                row_count INTEGER,
                column_count INTEGER
            )
        ''')
        
        # Analyses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Session metadata table (for storing JSON data)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS session_metadata (
                session_id TEXT PRIMARY KEY,
                analysis_data TEXT,
                outliers_data TEXT,
                correlations_data TEXT,
                semantic_types_data TEXT,
                ai_suggestions_data TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save a new session"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # Insert session basic info
            conn.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, filename, original_path, parquet_path, file_size, row_count, column_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                session_data.get('filename'),
                session_data.get('original_path'),
                session_data.get('parquet_path'),
                session_data.get('file_size'),
                session_data.get('dataframe_shape', (0, 0))[0],
                session_data.get('dataframe_shape', (0, 0))[1]
            ))
            
            # Insert session metadata (analysis results)
            conn.execute('''
                INSERT OR REPLACE INTO session_metadata
                (session_id, analysis_data, outliers_data, correlations_data, 
                 semantic_types_data, ai_suggestions_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                json.dumps(session_data.get('analysis', {})),
                json.dumps(session_data.get('outliers', {})),
                json.dumps(session_data.get('correlations', {})),
                json.dumps(session_data.get('semantic_types', {})),
                json.dumps(session_data.get('ai_suggestions', []))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by ID"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            # Get session basic info
            cursor = conn.execute(
                'SELECT * FROM sessions WHERE session_id = ?',
                (session_id,)
            )
            session_row = cursor.fetchone()
            
            if not session_row:
                conn.close()
                return None
            
            # Get session metadata
            cursor = conn.execute(
                'SELECT * FROM session_metadata WHERE session_id = ?',
                (session_id,)
            )
            metadata_row = cursor.fetchone()
            
            conn.close()
            
            # Construct session dict
            session_data = {
                'session_id': session_row['session_id'],
                'filename': session_row['filename'],
                'original_path': session_row['original_path'],
                'parquet_path': session_row['parquet_path'],
                'created_at': session_row['created_at'],
                'last_accessed': session_row['last_accessed'],
                'file_size': session_row['file_size'],
                'dataframe_shape': (session_row['row_count'], session_row['column_count'])
            }
            
            if metadata_row:
                session_data.update({
                    'analysis': json.loads(metadata_row['analysis_data']) if metadata_row['analysis_data'] else {},
                    'outliers': json.loads(metadata_row['outliers_data']) if metadata_row['outliers_data'] else {},
                    'correlations': json.loads(metadata_row['correlations_data']) if metadata_row['correlations_data'] else {},
                    'semantic_types': json.loads(metadata_row['semantic_types_data']) if metadata_row['semantic_types_data'] else {},
                    'ai_suggestions': json.loads(metadata_row['ai_suggestions_data']) if metadata_row['ai_suggestions_data'] else []
                })
            
            # Update last accessed time
            self.update_last_accessed(session_id)
            
            return session_data
            
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None
    
    def update_last_accessed(self, session_id: str):
        """Update last accessed timestamp"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                'UPDATE sessions SET last_accessed = CURRENT_TIMESTAMP WHERE session_id = ?',
                (session_id,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating last accessed: {e}")
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all sessions"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT session_id, filename, created_at, last_accessed, 
                       row_count, column_count, file_size
                FROM sessions 
                ORDER BY last_accessed DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated data"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # Delete from metadata
            conn.execute('DELETE FROM session_metadata WHERE session_id = ?', (session_id,))
            
            # Delete analyses
            conn.execute('DELETE FROM analyses WHERE session_id = ?', (session_id,))
            
            # Delete session
            conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def save_analysis(self, session_id: str, results: dict):
        """
        Save an analysis/result object for a given session_id.
        Stores analyses in backend/analyses.json grouped by session_id.
        """
        import json
        from pathlib import Path

        try:
            meta_path = Path(__file__).parent / "analyses.json"

            if meta_path.exists():
                with meta_path.open("r", encoding="utf-8") as f:
                    meta = json.load(f)
            else:
                meta = {}

            meta.setdefault(session_id, [])
            meta[session_id].append(results)

            with meta_path.open("w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # avoid crashing the app; log minimal info
            print(f"save_analysis error: {e}")

    def get_analyses(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all analyses for a session"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT * FROM analyses 
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
            
            analyses = []
            for row in cursor.fetchall():
                analyses.append({
                    'id': row['id'],
                    'analysis_type': row['analysis_type'],
                    'results': json.loads(row['results']) if row['results'] else {},
                    'created_at': row['created_at']
                })
            
            conn.close()
            return analyses
            
        except Exception as e:
            print(f"Error getting analyses: {e}")
            return []

# Global storage instance
storage = DataStorage()