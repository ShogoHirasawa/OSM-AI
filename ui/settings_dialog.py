"""
Settings dialog for OSM AI Agent plugin.
Allows users to configure OpenAI API key.
"""

from typing import Optional
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
)
from qgis.PyQt.QtCore import Qt

from ..core.settings import load_api_key, save_api_key, load_send_shortcut, save_send_shortcut


class SettingsDialog(QDialog):
    """Dialog for configuring plugin settings."""
    
    def __init__(self, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("OSM AI Agent - Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # API Key section
        api_key_label = QLabel("OpenAI API Key:")
        api_key_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(api_key_label)
        
        # Info text
        info_label = QLabel(
            "Enter your OpenAI API key to use the natural language query feature.\n"
            "You can get your API key from: https://platform.openai.com/api-keys"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info_label)
        
        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)
        
        # Show/Hide API key button
        show_hide_layout = QHBoxLayout()
        self.show_hide_button = QPushButton("Show API Key")
        self.show_hide_button.setMaximumWidth(120)
        self.show_hide_button.clicked.connect(self.toggle_api_key_visibility)
        show_hide_layout.addWidget(self.show_hide_button)
        show_hide_layout.addStretch()
        layout.addLayout(show_hide_layout)
        
        # Keyboard shortcut section
        shortcut_group = QGroupBox("Keyboard Shortcut")
        shortcut_layout = QVBoxLayout(shortcut_group)
        
        shortcut_label = QLabel("Send message with:")
        shortcut_layout.addWidget(shortcut_label)
        
        # Radio buttons for shortcut selection
        self.shortcut_group = QButtonGroup()
        
        self.enter_radio = QRadioButton("Enter")
        self.cmd_enter_radio = QRadioButton("Command+Enter (Ctrl+Enter on Windows/Linux)")
        
        self.shortcut_group.addButton(self.enter_radio, 0)
        self.shortcut_group.addButton(self.cmd_enter_radio, 1)
        
        shortcut_layout.addWidget(self.enter_radio)
        shortcut_layout.addWidget(self.cmd_enter_radio)
        
        layout.addWidget(shortcut_group)
        
        # Add stretch
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_hide_button.setText("Hide API Key")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_hide_button.setText("Show API Key")
    
    def load_settings(self):
        """Load existing settings."""
        # Load API key
        api_key = load_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
        
        # Load send shortcut (default to Enter)
        shortcut = load_send_shortcut()
        if shortcut == "cmd_enter":
            self.cmd_enter_radio.setChecked(True)
        else:
            self.enter_radio.setChecked(True)
    
    def save_and_close(self):
        """Save settings and close dialog."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            reply = QMessageBox.question(
                self,
                "Empty API Key",
                "Are you sure you want to save an empty API key?\n"
                "The plugin will not work without a valid API key.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Save API key
        save_api_key(api_key)
        
        # Save send shortcut
        if self.enter_radio.isChecked():
            save_send_shortcut("enter")
        else:
            save_send_shortcut("cmd_enter")
        
        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully!"
        )
        
        self.accept()

