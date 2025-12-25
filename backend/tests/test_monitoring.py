# backend/tests/test_monitoring.py
"""
Tests for error logging and monitoring functionality.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_simple_health_check(self):
        """Test the simple /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_health_check(self):
        """Test the /api/health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_detailed_health_check(self):
        """Test the detailed health check endpoint."""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "components" in data
        
        # Check components
        assert "database" in data["components"]
        assert "storage" in data["components"]
        assert "system" in data["components"]
        assert "error_tracking" in data["components"]
        assert "backups" in data["components"]
    
    def test_readiness_check(self):
        """Test the readiness probe endpoint."""
        response = client.get("/api/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
    
    def test_liveness_check(self):
        """Test the liveness probe endpoint."""
        response = client.get("/api/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] == True


class TestSentryIntegration:
    """Tests for Sentry integration utilities."""
    
    def test_init_sentry_without_dsn(self):
        """Test that Sentry init returns False when DSN is not configured."""
        from utils.sentry_integration import init_sentry
        
        with patch('utils.sentry_integration.settings') as mock_settings:
            mock_settings.SENTRY_DSN = ""
            result = init_sentry()
            assert result == False
    
    def test_capture_exception_without_dsn(self):
        """Test that capture_exception returns None when DSN is not configured."""
        from utils.sentry_integration import capture_exception
        
        with patch('utils.sentry_integration.settings') as mock_settings:
            mock_settings.SENTRY_DSN = ""
            result = capture_exception(Exception("test"))
            assert result is None
    
    def test_capture_message_without_dsn(self):
        """Test that capture_message returns None when DSN is not configured."""
        from utils.sentry_integration import capture_message
        
        with patch('utils.sentry_integration.settings') as mock_settings:
            mock_settings.SENTRY_DSN = ""
            result = capture_message("test message")
            assert result is None


class TestDatabaseBackup:
    """Tests for database backup functionality."""
    
    def test_backup_manager_initialization(self):
        """Test that backup manager initializes correctly."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = Path(tmpdir) / "backups"
                mock_settings.BACKUP_RETENTION_DAYS = 7
                mock_settings.BACKUP_ENABLED = True
                mock_settings.IS_POSTGRES = False
                
                backup = DatabaseBackup()
                assert backup.backup_dir.exists()
    
    def test_generate_backup_filename(self):
        """Test backup filename generation."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = Path(tmpdir)
                mock_settings.BACKUP_RETENTION_DAYS = 7
                
                backup = DatabaseBackup()
                filename = backup._generate_backup_filename("test")
                
                assert filename.startswith("test_")
                assert len(filename) > 5  # test_ + timestamp
    
    def test_list_backups_empty(self):
        """Test listing backups when directory is empty."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = Path(tmpdir)
                mock_settings.BACKUP_RETENTION_DAYS = 7
                
                backup = DatabaseBackup()
                backups = backup.list_backups()
                
                assert backups == []
    
    def test_get_backup_status(self):
        """Test getting backup status."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = Path(tmpdir)
                mock_settings.BACKUP_RETENTION_DAYS = 7
                mock_settings.BACKUP_ENABLED = True
                mock_settings.IS_POSTGRES = False
                
                backup = DatabaseBackup()
                status = backup.get_backup_status()
                
                assert "enabled" in status
                assert "backup_dir" in status
                assert "retention_days" in status
                assert "database_type" in status
                assert "backup_count" in status
    
    def test_backup_disabled(self):
        """Test that backup returns None when disabled."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = Path(tmpdir)
                mock_settings.BACKUP_RETENTION_DAYS = 7
                mock_settings.BACKUP_ENABLED = False
                mock_settings.IS_POSTGRES = False
                
                backup = DatabaseBackup()
                result = backup.create_backup()
                
                assert result is None
    
    def test_sqlite_backup(self):
        """Test SQLite backup creation."""
        from utils.backup import DatabaseBackup
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake SQLite database file
            db_path = Path(tmpdir) / "test.db"
            db_path.write_text("fake database content")
            
            backup_dir = Path(tmpdir) / "backups"
            
            with patch('utils.backup.settings') as mock_settings:
                mock_settings.BACKUP_DIR = backup_dir
                mock_settings.BACKUP_RETENTION_DAYS = 7
                mock_settings.BACKUP_ENABLED = True
                mock_settings.IS_POSTGRES = False
                mock_settings.DATABASE_PATH = db_path
                
                backup = DatabaseBackup()
                result = backup.backup_sqlite()
                
                assert result is not None
                assert result.exists()
                assert "sqlite" in result.name
