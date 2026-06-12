"""
Unit tests for DropZoneWidget drag-and-drop functionality
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QUrl, QMimeData, Qt, QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent
from PySide6.QtWidgets import QApplication

from configcrypt.gui.main_window import DropZoneWidget


@pytest.fixture
def app():
    """Create QApplication instance for tests"""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def drop_zone(app):
    """Create DropZoneWidget instance"""
    widget = DropZoneWidget()
    return widget


class TestDragEnterEvent:
    """Tests for dragEnterEvent method"""

    def test_accepts_single_local_file(self, drop_zone, tmp_path):
        """Test that dragEnterEvent accepts a single local file"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data with file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify event was accepted
        event.acceptProposedAction.assert_called_once()

        # Verify drag active state was set
        assert drop_zone.property("dragActive") == "true"

    def test_rejects_directory(self, drop_zone, tmp_path):
        """Test that dragEnterEvent rejects directories"""
        # Create a test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create mime data with directory URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_dir))])

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify event was rejected
        event.ignore.assert_called_once()
        event.acceptProposedAction.assert_not_called()

    def test_rejects_multiple_files(self, drop_zone, tmp_path):
        """Test that dragEnterEvent rejects multiple files"""
        # Create test files
        test_file1 = tmp_path / "test1.txt"
        test_file1.write_text("content 1")
        test_file2 = tmp_path / "test2.txt"
        test_file2.write_text("content 2")

        # Create mime data with multiple file URLs
        mime_data = QMimeData()
        mime_data.setUrls(
            [QUrl.fromLocalFile(str(test_file1)), QUrl.fromLocalFile(str(test_file2))]
        )

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify event was rejected
        event.ignore.assert_called_once()
        event.acceptProposedAction.assert_not_called()

    def test_rejects_non_local_urls(self, drop_zone):
        """Test that dragEnterEvent rejects non-local URLs (e.g., http://)"""
        # Create mime data with non-local URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl("http://example.com/file.txt")])

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify event was rejected
        event.ignore.assert_called_once()
        event.acceptProposedAction.assert_not_called()

    def test_rejects_no_urls(self, drop_zone):
        """Test that dragEnterEvent rejects when no URLs are present"""
        # Create mime data without URLs
        mime_data = QMimeData()
        mime_data.setText("some text")

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify event was rejected
        event.ignore.assert_called_once()
        event.acceptProposedAction.assert_not_called()

    def test_visual_feedback_applied(self, drop_zone, tmp_path):
        """Test that visual feedback is applied when drag enters"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data with file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dragEnterEvent(event)

        # Verify style was updated
        drop_zone.style().unpolish.assert_called_once_with(drop_zone)
        drop_zone.style().polish.assert_called_once_with(drop_zone)


class TestDragLeaveEvent:
    """Tests for dragLeaveEvent method"""

    def test_clears_drag_active_state(self, drop_zone):
        """Test that dragLeaveEvent clears the drag active state"""
        # Set drag active state first
        drop_zone.setProperty("dragActive", "true")

        # Create drag leave event
        event = MagicMock(spec=QDragLeaveEvent)

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dragLeaveEvent(event)

        # Verify drag active state was cleared
        assert drop_zone.property("dragActive") == "false"

    def test_visual_feedback_removed(self, drop_zone):
        """Test that visual feedback is removed when drag leaves"""
        # Set drag active state first
        drop_zone.setProperty("dragActive", "true")

        # Create drag leave event
        event = MagicMock(spec=QDragLeaveEvent)

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dragLeaveEvent(event)

        # Verify style was updated
        drop_zone.style().unpolish.assert_called_once_with(drop_zone)
        drop_zone.style().polish.assert_called_once_with(drop_zone)


class TestDropEvent:
    """Tests for dropEvent method"""

    def test_emits_signal_for_valid_file(self, drop_zone, tmp_path, qtbot):
        """Test that dropEvent emits file_dropped signal for valid file"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data with file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Connect signal spy
        with qtbot.waitSignal(drop_zone.file_dropped, timeout=1000) as blocker:
            drop_zone.dropEvent(event)

        # Verify signal was emitted with correct path
        assert blocker.args[0] == test_file

        # Verify event was accepted
        event.acceptProposedAction.assert_called_once()

    def test_clears_drag_active_state_on_drop(self, drop_zone, tmp_path):
        """Test that dropEvent clears drag active state"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Set drag active state first
        drop_zone.setProperty("dragActive", "true")

        # Create mime data with file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dropEvent(event)

        # Verify drag active state was cleared
        assert drop_zone.property("dragActive") == "false"

    def test_visual_feedback_removed_on_drop(self, drop_zone, tmp_path):
        """Test that visual feedback is removed on drop"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data with file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dropEvent(event)

        # Verify style was updated
        drop_zone.style().unpolish.assert_called_once_with(drop_zone)
        drop_zone.style().polish.assert_called_once_with(drop_zone)

    @patch("keyvault.gui.main_window.QMessageBox")
    def test_shows_warning_for_directory(self, mock_msgbox, drop_zone, tmp_path):
        """Test that dropEvent shows warning for directory"""
        # Create a test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create mime data with directory URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_dir))])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method
        drop_zone.dropEvent(event)

        # Verify warning was shown
        mock_msgbox.warning.assert_called_once()
        assert "无效文件" in mock_msgbox.warning.call_args[0][1]

        # Verify event was not accepted
        event.acceptProposedAction.assert_not_called()

    def test_handles_non_local_url_gracefully(self, drop_zone):
        """Test that dropEvent handles non-local URLs gracefully"""
        # Create mime data with non-local URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl("http://example.com/file.txt")])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method - should not raise exception
        drop_zone.dropEvent(event)

        # Verify event was not accepted (no local file)
        event.acceptProposedAction.assert_not_called()

    def test_handles_empty_urls_gracefully(self, drop_zone):
        """Test that dropEvent handles empty URL list gracefully"""
        # Create mime data with empty URL list
        mime_data = QMimeData()
        mime_data.setUrls([])

        # Create drop event
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Call the method - should not raise exception
        drop_zone.dropEvent(event)

        # Verify event was not accepted
        event.acceptProposedAction.assert_not_called()


class TestDragDropIntegration:
    """Integration tests for complete drag-and-drop workflow"""

    def test_complete_drag_drop_workflow(self, drop_zone, tmp_path, qtbot):
        """Test complete workflow: drag enter -> drag leave"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Mock the style methods
        drop_zone.style = MagicMock()

        # 1. Drag enter
        enter_event = MagicMock(spec=QDragEnterEvent)
        enter_event.mimeData.return_value = mime_data
        drop_zone.dragEnterEvent(enter_event)

        # Verify drag active
        assert drop_zone.property("dragActive") == "true"
        enter_event.acceptProposedAction.assert_called_once()

        # 2. Drag leave
        leave_event = MagicMock(spec=QDragLeaveEvent)
        drop_zone.dragLeaveEvent(leave_event)

        # Verify drag no longer active
        assert drop_zone.property("dragActive") == "false"

    def test_drag_enter_drop_workflow(self, drop_zone, tmp_path, qtbot):
        """Test workflow: drag enter -> drop"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Create mime data
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Mock the style methods
        drop_zone.style = MagicMock()

        # 1. Drag enter
        enter_event = MagicMock(spec=QDragEnterEvent)
        enter_event.mimeData.return_value = mime_data
        drop_zone.dragEnterEvent(enter_event)

        # Verify drag active
        assert drop_zone.property("dragActive") == "true"

        # 2. Drop
        drop_event = MagicMock(spec=QDropEvent)
        drop_event.mimeData.return_value = mime_data

        with qtbot.waitSignal(drop_zone.file_dropped, timeout=1000) as blocker:
            drop_zone.dropEvent(drop_event)

        # Verify signal emitted and drag no longer active
        assert blocker.args[0] == test_file
        assert drop_zone.property("dragActive") == "false"
        drop_event.acceptProposedAction.assert_called_once()

    def test_accepts_drops_is_enabled(self, drop_zone):
        """Test that acceptDrops is enabled on the widget"""
        assert drop_zone.acceptDrops() is True


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_handles_nonexistent_file_path(self, drop_zone):
        """Test handling of URL pointing to nonexistent file"""
        # Create mime data with nonexistent file URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile("/nonexistent/file.txt")])

        # Create drag enter event
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data

        # Call the method - should reject gracefully
        drop_zone.dragEnterEvent(event)

        # Verify event was rejected
        event.ignore.assert_called_once()

    def test_handles_unicode_filenames(self, drop_zone, tmp_path, qtbot):
        """Test handling of files with Unicode characters in name"""
        # Create file with Unicode name
        test_file = tmp_path / "测试文件.txt"
        test_file.write_text("test content")

        # Create mime data
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Test drag enter
        enter_event = MagicMock(spec=QDragEnterEvent)
        enter_event.mimeData.return_value = mime_data
        drop_zone.dragEnterEvent(enter_event)

        enter_event.acceptProposedAction.assert_called_once()

        # Test drop
        drop_event = MagicMock(spec=QDropEvent)
        drop_event.mimeData.return_value = mime_data

        with qtbot.waitSignal(drop_zone.file_dropped, timeout=1000) as blocker:
            drop_zone.dropEvent(drop_event)

        assert blocker.args[0] == test_file

    def test_handles_spaces_in_filename(self, drop_zone, tmp_path, qtbot):
        """Test handling of files with spaces in name"""
        # Create file with spaces
        test_file = tmp_path / "test file with spaces.txt"
        test_file.write_text("test content")

        # Create mime data
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(test_file))])

        # Mock the style methods
        drop_zone.style = MagicMock()

        # Test drop
        drop_event = MagicMock(spec=QDropEvent)
        drop_event.mimeData.return_value = mime_data

        with qtbot.waitSignal(drop_zone.file_dropped, timeout=1000) as blocker:
            drop_zone.dropEvent(drop_event)

        assert blocker.args[0] == test_file
