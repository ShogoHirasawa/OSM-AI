"""
OSM AI Agent - QGIS Plugin
Main plugin implementation that connects UI with core functionality.
"""

import os
from pathlib import Path

from qgis.PyQt.QtCore import Qt, QEvent, QObject, QSettings, QTimer, QPropertyAnimation, pyqtProperty, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QPixmap, QKeyEvent, QColor
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QMessageBox, 
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QTabBar, QApplication
)
from qgis.core import Qgis

from .ui.osm_ai_form import Ui_QuickOSMAIDockBase
from .ui.settings_dialog import SettingsDialog
from .core.llm_client import call_llm_for_overpass
from .core.overpass_client import fetch_osm_geojson
from .core.qgis_utils import get_current_bbox_wgs84, add_geojson_layer


def get_qgis_language():
    """
    Get current QGIS language code.
    
    Returns:
        Language code (e.g., 'ja', 'en', 'zh')
    """
    locale = QSettings().value('locale/userLocale', 'en_US')
    return locale.split('_')[0] if locale else 'en'


def get_welcome_message():
    """
    Get welcome message in user's language based on QGIS locale.
    
    Returns:
        Localized welcome message string
    """
    lang = get_qgis_language()
    
    # Welcome messages in different languages
    messages = {
        'ja': 'OSM AI です。\n取得したい OSM データを教えてください。',
        'en': 'OSM AI here.\nTell me what OSM data to load.',
        'zh': 'OSM AI 在这里。\n告诉我要加载什么 OSM 数据。',
        'es': 'OSM AI aquí.\nDime qué datos OSM cargar.',
        'fr': 'OSM AI ici.\nDites-moi quelles données OSM charger.',
        'de': 'OSM AI hier.\nSagen Sie mir, welche OSM-Daten geladen werden sollen.',
        'it': 'OSM AI qui.\nDimmi quali dati OSM caricare.',
        'pt': 'OSM AI aqui.\nDiga-me quais dados OSM carregar.',
        'ru': 'OSM AI здесь.\nСкажите, какие данные OSM загрузить.',
        'ko': 'OSM AI입니다.\n로드할 OSM 데이터를 알려주세요.',
    }
    
    return messages.get(lang, messages['en'])


def get_placeholder_text():
    """
    Get placeholder text for input box in user's language.
    
    Returns:
        Localized placeholder text string
    """
    lang = get_qgis_language()
    
    # Placeholder texts in different languages
    placeholders = {
        'ja': '例：東京都渋谷区のコンビニを取得',
        'en': 'e.g., Get all convenience stores in Shibuya, Tokyo',
        'zh': '例如：获取东京涩谷的所有便利店',
        'es': 'ej.: Obtener todas las tiendas de conveniencia en Shibuya, Tokio',
        'fr': 'ex. : Obtenir tous les dépanneurs à Shibuya, Tokyo',
        'de': 'z.B.: Alle Convenience-Stores in Shibuya, Tokio abrufen',
        'it': 'es.: Ottieni tutti i minimarket a Shibuya, Tokyo',
        'pt': 'ex.: Obter todas as lojas de conveniência em Shibuya, Tóquio',
        'ru': 'напр.: Получить все круглосуточные магазины в Сибуя, Токио',
        'ko': '예: 도쿄 시부야의 모든 편의점 가져오기',
    }
    
    return placeholders.get(lang, placeholders['en'])


def get_thinking_message():
    """
    Get thinking/processing message in user's language.
    
    Returns:
        Localized thinking message string
    """
    lang = get_qgis_language()
    
    # Thinking messages in different languages
    messages = {
        'ja': '考え中...',
        'en': 'Thinking...',
        'zh': '思考中...',
        'es': 'Pensando...',
        'fr': 'Réflexion...',
        'de': 'Nachdenken...',
        'it': 'Pensando...',
        'pt': 'Pensando...',
        'ru': 'Думаю...',
        'ko': '생각 중...',
    }
    
    return messages.get(lang, messages['en'])


class OsmAiPlugin(QObject):
    """QGIS Plugin Implementation for OSM AI Agent."""
    
    def __init__(self, iface):
        """
        Constructor.
        
        Args:
            iface: An interface instance that will be passed to this class
                   which provides the hook by which you can manipulate the QGIS
                   application at run time.
        """
        super().__init__()
        self.iface = iface
        self.plugin_dir = Path(__file__).parent
        
        # Initialize plugin components
        self.actions = []
        self.menu = "OSM AI Agent"
        self.toolbar = None
        self.dock_widget = None
        self.ui = None
        
        # Tab management
        self.chat_tabs = {}  # tab_index -> {"history": [], "widgets": []}
        self.current_tab_index = 0
        self.next_tab_id = 1
        
        # Thinking message widget
        self.thinking_widget = None
        self.thinking_timer = None
        self.thinking_state = 0
        
        # Settings
        from .core.settings import load_send_shortcut
        self.send_shortcut = load_send_shortcut()  # "enter" or "cmd_enter"
    
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        # Create icon
        icon_path = self.plugin_dir / "icon.png"
        if not icon_path.exists():
            # Use a default icon if custom icon doesn't exist
            icon = QIcon()
        else:
            icon = QIcon(str(icon_path))
        
        # Create main action
        action = QAction(
            icon,
            "Open OSM AI Agent",
            self.iface.mainWindow()
        )
        action.triggered.connect(self.show_dock)
        action.setEnabled(True)
        action.setCheckable(True)
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.menu, action)
        
        self.actions.append(action)
        
        # Create settings action
        settings_action = QAction(
            "Settings",
            self.iface.mainWindow()
        )
        settings_action.triggered.connect(self.show_settings)
        self.iface.addPluginToMenu(self.menu, settings_action)
        self.actions.append(settings_action)
        
        # Create dock widget
        self._create_dock_widget()
    
    def _create_dock_widget(self):
        """Create and setup the dock widget."""
        
        # Create dock widget
        self.dock_widget = QDockWidget("OSM AI", self.iface.mainWindow())
        self.dock_widget.setObjectName("OsmAiAgentDock")
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Setup UI from form
        self.ui = Ui_QuickOSMAIDockBase()
        self.ui.setupUi(self.dock_widget)
        
        # Setup icons
        self._setup_icons()
        
        # Setup tab close icon
        self._setup_tab_close_icon()
        
        # Set localized placeholder text
        self.ui.inputEdit.setPlaceholderText(get_placeholder_text())
        
        # Connect signals
        self.ui.sendButton.clicked.connect(self.on_send_clicked)
        self.ui.newChatButton.clicked.connect(self.on_new_chat_clicked)
        self.ui.chatTabs.tabCloseRequested.connect(self.on_tab_close_requested)
        self.ui.chatTabs.currentChanged.connect(self.on_tab_changed)
        
        # Install event filter for keyboard shortcuts
        self.ui.inputEdit.installEventFilter(self)
        
        # Connect dock widget closed signal to uncheck menu action
        self.dock_widget.visibilityChanged.connect(self._dock_visibility_changed)
        
        # Clear placeholder tab
        self.ui.chatTabs.clear()
        
        # Create initial tab
        self._create_new_tab()
        
        # Add dock widget to QGIS interface
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        
        # Hide by default
        self.dock_widget.hide()
    
    def _dock_visibility_changed(self, visible):
        """Handle dock widget visibility changes."""
        if self.actions:
            self.actions[0].setChecked(visible)
    
    def _setup_icons(self):
        """Setup icons for UI elements."""
        # Set icon for new chat button
        plus_icon_path = self.plugin_dir / "ui" / "icon" / "plus.svg"
        if plus_icon_path.exists():
            self.ui.newChatButton.setIcon(QIcon(str(plus_icon_path)))
            self.ui.newChatButton.setText("")
        
        # Set icon for send button
        sent_icon_path = self.plugin_dir / "ui" / "icon" / "sent.svg"
        if sent_icon_path.exists():
            self.ui.sendButton.setIcon(QIcon(str(sent_icon_path)))
        self.ui.sendButton.setText("Send")
    
    def _setup_tab_close_icon(self):
        """Setup tab close icon using xmark.svg."""
        xmark_icon_path = self.plugin_dir / "ui" / "icon" / "xmark.svg"
        if xmark_icon_path.exists():
            # Set the tab bar button icon
            from qgis.PyQt.QtWidgets import QTabBar
            tab_bar = self.ui.chatTabs.tabBar()
            
            # Set custom stylesheet for close button
            self.ui.chatTabs.setStyleSheet(f"""
                QTabBar::close-button {{
                    image: url({xmark_icon_path});
                    subcontrol-position: right;
                }}
            """)
    
    def _add_message_to_ui(self, message: str, is_user: bool):
        """
        Add a message to the chat UI.
        
        Args:
            message: The message text
            is_user: True if message is from user, False if from AI
        """
        # Create message widget
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(8, 4, 8, 4)
        message_layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setScaledContents(True)
        
        if is_user:
            icon_path = self.plugin_dir / "ui" / "icon" / "user.svg"
            message_layout.addStretch()
        else:
            icon_path = self.plugin_dir / "ui" / "icon" / "agent.svg"
        
        if icon_path.exists():
            icon_label.setPixmap(QIcon(str(icon_path)).pixmap(32, 32))
        
        # Message bubble
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        # Fixed width, variable height based on content
        message_label.setFixedWidth(280)
        message_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        message_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Layout
        if is_user:
            message_layout.addWidget(message_label)
            message_layout.addWidget(icon_label, 0, Qt.AlignTop)
        else:
            message_layout.addWidget(icon_label, 0, Qt.AlignTop)
            message_layout.addWidget(message_label)
            message_layout.addStretch()
        
        # Add to message container
        self.ui.messageLayout.addWidget(message_widget)
        
        # Force layout update and scroll to bottom
        from qgis.PyQt.QtCore import QTimer
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """Scroll message area to bottom."""
        scrollbar = self.ui.messageScrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _show_thinking_message(self):
        """Show animated thinking message."""
        # Create thinking widget
        self.thinking_widget = QWidget()
        thinking_layout = QHBoxLayout(self.thinking_widget)
        thinking_layout.setContentsMargins(8, 4, 8, 4)
        thinking_layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setScaledContents(True)
        icon_path = self.plugin_dir / "ui" / "icon" / "agent.svg"
        if icon_path.exists():
            icon_label.setPixmap(QIcon(str(icon_path)).pixmap(32, 32))
        
        # Thinking message
        self.thinking_label = QLabel(get_thinking_message())
        self.thinking_label.setWordWrap(True)
        self.thinking_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1976d2;
            }
        """)
        self.thinking_label.setFixedWidth(280)
        self.thinking_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        
        thinking_layout.addWidget(icon_label, 0, Qt.AlignTop)
        thinking_layout.addWidget(self.thinking_label)
        thinking_layout.addStretch()
        
        # Add to message container
        self.ui.messageLayout.addWidget(self.thinking_widget)
        self._scroll_to_bottom()
        
        # Start animation timer
        self.thinking_state = 0
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self._animate_thinking)
        self.thinking_timer.start(500)  # Update every 500ms
    
    def _animate_thinking(self):
        """Animate thinking message with color gradient."""
        if not self.thinking_label:
            return
        
        # Cycle through colors
        colors = [
            "#e3f2fd",  # Light blue
            "#bbdefb",  # Medium blue
            "#90caf9",  # Blue
            "#bbdefb",  # Medium blue
        ]
        
        self.thinking_state = (self.thinking_state + 1) % len(colors)
        color = colors[self.thinking_state]
        
        self.thinking_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1976d2;
            }}
        """)
    
    def _hide_thinking_message(self):
        """Hide and remove thinking message."""
        if self.thinking_timer:
            self.thinking_timer.stop()
            self.thinking_timer = None
        
        if self.thinking_widget:
            self.ui.messageLayout.removeWidget(self.thinking_widget)
            self.thinking_widget.deleteLater()
            self.thinking_widget = None
            self.thinking_label = None
    
    def _update_thinking_message(self, message: str):
        """Update thinking message text."""
        if self.thinking_label:
            self.thinking_label.setText(message)
    
    def _clear_messages(self):
        """Clear all messages from the UI."""
        # Remove all widgets from message layout
        while self.ui.messageLayout.count():
            item = self.ui.messageLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _create_new_tab(self):
        """Create a new chat tab."""
        tab_id = self.next_tab_id
        self.next_tab_id += 1
        
        # Create tab data
        self.chat_tabs[tab_id] = {
            "history": [],
            "widgets": []
        }
        
        # Add tab to UI
        tab_widget = QWidget()
        tab_index = self.ui.chatTabs.addTab(tab_widget, f"Chat {tab_id}")
        
        # Switch to new tab
        self.ui.chatTabs.setCurrentIndex(tab_index)
        self.current_tab_index = tab_id
        
        # Clear current messages and show welcome
        self._clear_messages()
        welcome_message = get_welcome_message()
        self._add_message_to_ui(welcome_message, is_user=False)
        
        # Add welcome message to tab history
        self.chat_tabs[tab_id]["history"].append({
            "role": "assistant",
            "content": welcome_message
        })
        
        return tab_id
    
    def _get_current_tab_data(self):
        """Get data for current tab."""
        if self.current_tab_index not in self.chat_tabs:
            self._create_new_tab()
        return self.chat_tabs[self.current_tab_index]
    
    def on_tab_changed(self, index):
        """Handle tab switch."""
        if index < 0:
            return
        
        # Get tab ID from tab text (e.g., "Chat 1" -> 1)
        tab_text = self.ui.chatTabs.tabText(index)
        try:
            tab_id = int(tab_text.split()[-1])
        except:
            return
        
        if tab_id not in self.chat_tabs:
            return
        
        self.current_tab_index = tab_id
        
        # Clear current messages
        self._clear_messages()
        
        # Restore messages from tab history
        tab_data = self.chat_tabs[tab_id]
        for msg in tab_data["history"]:
            self._add_message_to_ui(msg["content"], msg["role"] == "user")
    
    def on_tab_close_requested(self, index):
        """Handle tab close request."""
        # Don't allow closing the last tab
        if self.ui.chatTabs.count() <= 1:
            return
        
        # Get tab ID
        tab_text = self.ui.chatTabs.tabText(index)
        try:
            tab_id = int(tab_text.split()[-1])
        except:
            return
        
        # Remove tab data
        if tab_id in self.chat_tabs:
            del self.chat_tabs[tab_id]
        
        # Remove tab from UI
        self.ui.chatTabs.removeTab(index)
    
    def show_dock(self):
        """Show or hide the dock widget."""
        if self.dock_widget:
            if self.dock_widget.isVisible():
                self.dock_widget.hide()
            else:
                self.dock_widget.show()
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.iface.mainWindow())
        if dialog.exec_():
            # Reload settings
            from .core.settings import load_send_shortcut
            self.send_shortcut = load_send_shortcut()
    
    def eventFilter(self, obj, event):
        """Event filter for keyboard shortcuts."""
        if obj == self.ui.inputEdit and event.type() == QEvent.KeyPress:
            key_event = event
            
            # Check for Enter or Cmd+Enter
            if self.send_shortcut == "enter":
                # Enter alone sends message
                if key_event.key() == Qt.Key_Return and key_event.modifiers() == Qt.NoModifier:
                    self.on_send_clicked()
                    return True
            elif self.send_shortcut == "cmd_enter":
                # Cmd+Enter (or Ctrl+Enter on other platforms) sends message
                if key_event.key() == Qt.Key_Return and (
                    key_event.modifiers() == Qt.ControlModifier or 
                    key_event.modifiers() == Qt.MetaModifier
                ):
                    self.on_send_clicked()
                    return True
        
        return QObject.eventFilter(self, obj, event)
    
    def on_new_chat_clicked(self):
        """Handle new chat button click."""
        self._create_new_tab()
        self.ui.inputEdit.clear()
    
    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        
        # Remove dock widget
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)
            self.dock_widget.deleteLater()
            self.dock_widget = None
        
        # Remove actions
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        
        self.actions = []
    
    def on_send_clicked(self):
        """Handle send button click event."""
        
        try:
            # Get user message from input
            user_message = self.ui.inputEdit.toPlainText().strip()
            
            if not user_message:
                self._show_warning("Please enter a query.")
                return
            
            # Get current tab data
            tab_data = self._get_current_tab_data()
            
            # Display user message in UI
            self._add_message_to_ui(user_message, is_user=True)
            
            # Add user message to tab history
            tab_data["history"].append({
                "role": "user",
                "content": user_message
            })
            
            # Clear input immediately
            self.ui.inputEdit.clear()
            
            # Show thinking message
            self._show_thinking_message()
            
            # Force UI update
            QApplication.processEvents()
            
            # Step 1: Get current bbox
            bbox = get_current_bbox_wgs84()
            
            # Step 2: Call LLM with user's language
            user_lang = get_qgis_language()
            llm_result = call_llm_for_overpass(user_message, bbox, tab_data["history"], user_lang)
            
            # Hide thinking message
            self._hide_thinking_message()
            
            # Force UI update
            QApplication.processEvents()
            
            # Check mode
            mode = llm_result.get("mode", "query")
            
            if mode == "chat":
                # Chat mode: display message and continue conversation
                ai_message = llm_result.get("message", "")
                
                # Display AI message in UI
                self._add_message_to_ui(ai_message, is_user=False)
                
                # Add to tab history
                tab_data["history"].append({
                    "role": "assistant",
                    "content": ai_message
                })
                
            elif mode == "query":
                # Query mode: execute Overpass query
                description = llm_result.get("description", "OSM Data")
                overpass_query = llm_result["overpass_query"]
                
                # Display AI message
                ai_message = f"Fetching: {description}"
                self._add_message_to_ui(ai_message, is_user=False)
                
                # Add to tab history
                tab_data["history"].append({
                    "role": "assistant",
                    "content": f"Executing query: {description}"
                })
                
                # Step 3: Fetch OSM data
                # Show fetching message
                self._update_thinking_message("Fetching data...")
                QApplication.processEvents()
                
                geojson_str = fetch_osm_geojson(overpass_query)
                
                # Step 4: Add layer to QGIS
                add_geojson_layer(geojson_str, description)
                
                # Success message in UI
                success_message = f"✓ Successfully added layer: {description}"
                self._add_message_to_ui(success_message, is_user=False)
                
                # Add success to tab history
                tab_data["history"].append({
                    "role": "assistant",
                    "content": success_message
                })
                
                # Show success in message bar
                self._show_success(f"Successfully added layer: {description}")
            
        except RuntimeError as e:
            self._hide_thinking_message()
            self._show_error(f"Error: {str(e)}")
        except Exception as e:
            self._hide_thinking_message()
            self._show_error(f"Unexpected error: {str(e)}")
    
    def _show_info(self, message: str):
        """Show info message in QGIS message bar."""
        self.iface.messageBar().pushMessage(
            "OSM AI Agent",
            message,
            level=Qgis.Info,
            duration=3
        )
    
    def _show_success(self, message: str):
        """Show success message in QGIS message bar."""
        self.iface.messageBar().pushMessage(
            "OSM AI Agent",
            message,
            level=Qgis.Success,
            duration=5
        )
    
    def _show_warning(self, message: str):
        """Show warning message in QGIS message bar."""
        self.iface.messageBar().pushMessage(
            "OSM AI Agent",
            message,
            level=Qgis.Warning,
            duration=5
        )
    
    def _show_error(self, message: str):
        """Show error message in QGIS message bar."""
        self.iface.messageBar().pushMessage(
            "OSM AI Agent",
            message,
            level=Qgis.Critical,
            duration=10
        )

