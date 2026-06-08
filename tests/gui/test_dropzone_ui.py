"""
Unit tests for DropZoneWidget UI elements
"""

import pytest
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

from configcrypt.gui.main_window import DropZoneWidget


@pytest.fixture
def drop_zone(qtbot):
    """Create a DropZoneWidget instance for testing"""
    widget = DropZoneWidget()
    qtbot.addWidget(widget)
    return widget


def test_dropzone_displays_file_icon(drop_zone):
    """
    Verify that the drag zone displays a file icon
    
    Requirements verified:
    - Drag zone displays an icon (file icon emoji)
    """
    # Find the icon label (first QLabel with emoji)
    layout = drop_zone.layout()
    icon_label = None
    
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() and isinstance(item.widget(), QLabel):
            label = item.widget()
            if "📁" in label.text():
                icon_label = label
                break
    
    assert icon_label is not None, "File icon label not found"
    assert icon_label.text() == "📁", "Icon should be a file emoji"
    
    # Verify icon is large (48pt)
    font = icon_label.font()
    assert font.pointSize() == 48, "Icon font size should be 48pt"
    
    # Verify icon is centered
    assert icon_label.alignment() & Qt.AlignmentFlag.AlignCenter


def test_dropzone_displays_hint_text(drop_zone):
    """
    Verify that the drag zone displays hint text
    
    Requirements verified:
    - Drag zone displays hint text (e.g., "拖拽文件到此处")
    - Text is clear and informative
    """
    # Find the main hint label
    layout = drop_zone.layout()
    hint_label = None
    
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() and isinstance(item.widget(), QLabel):
            label = item.widget()
            if "拖拽文件到此处" in label.text():
                hint_label = label
                break
    
    assert hint_label is not None, "Hint text label not found"
    assert hint_label.text() == "拖拽文件到此处", "Hint text should be '拖拽文件到此处'"
    
    # Verify text is large and bold
    font = hint_label.font()
    assert font.pointSize() == 16, "Hint font size should be 16pt"
    assert font.bold(), "Hint text should be bold"
    
    # Verify text is centered
    assert hint_label.alignment() & Qt.AlignmentFlag.AlignCenter


def test_dropzone_displays_secondary_hint(drop_zone):
    """
    Verify that the drag zone displays secondary hint text
    
    Requirements verified:
    - UI has proper layout and styling
    - Text is clear and informative
    """
    # Find the secondary hint label
    layout = drop_zone.layout()
    sub_hint = None
    
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() and isinstance(item.widget(), QLabel):
            label = item.widget()
            if "支持加密明文文件或解密" in label.text():
                sub_hint = label
                break
    
    assert sub_hint is not None, "Secondary hint label not found"
    assert "支持加密明文文件或解密 .enc 文件" in sub_hint.text()
    
    # Verify text is centered
    assert sub_hint.alignment() & Qt.AlignmentFlag.AlignCenter


def test_dropzone_has_proper_layout(drop_zone):
    """
    Verify that the drag zone has proper layout and styling
    
    Requirements verified:
    - UI has proper layout and styling
    """
    # Verify the widget has a layout
    layout = drop_zone.layout()
    assert layout is not None, "DropZoneWidget should have a layout"
    assert isinstance(layout, QVBoxLayout), "Layout should be QVBoxLayout"
    
    # Verify layout alignment
    assert layout.alignment() & Qt.AlignmentFlag.AlignCenter
    
    # Verify layout spacing
    assert layout.spacing() == 20, "Layout spacing should be 20"


def test_dropzone_has_add_file_button(drop_zone):
    """
    Verify that the drag zone has an add file button
    
    Requirements verified:
    - UI has proper layout and styling
    """
    # Find the add file button
    layout = drop_zone.layout()
    add_button = None
    
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() and isinstance(item.widget(), QPushButton):
            button = item.widget()
            if "添加文件" in button.text():
                add_button = button
                break
    
    assert add_button is not None, "Add file button not found"
    assert "📁" in add_button.text(), "Button should have file icon"
    assert add_button.minimumWidth() == 200
    assert add_button.minimumHeight() == 50


def test_dropzone_ui_elements_order(drop_zone):
    """
    Verify that UI elements are in the correct order
    
    Requirements verified:
    - UI has proper layout and styling
    """
    layout = drop_zone.layout()
    
    # Collect all widget texts in order
    widgets_order = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget():
            widget = item.widget()
            if isinstance(widget, QLabel):
                widgets_order.append(widget.text())
            elif isinstance(widget, QPushButton):
                widgets_order.append(widget.text())
    
    # Verify the order: icon -> main hint -> sub hint -> add button
    # (ignore stretches and button layout)
    assert "📁" in widgets_order[0], "First element should be file icon"
    assert "拖拽文件到此处" in widgets_order[1], "Second element should be main hint"
    assert "支持加密" in widgets_order[2], "Third element should be secondary hint"
