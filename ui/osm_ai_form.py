"""
Auto-generated UI form code for OSM AI Agent plugin.
This file is equivalent to running pyuic on osm_ai.ui
"""

from qgis.PyQt import QtCore, QtGui, QtWidgets


class Ui_QuickOSMAIDockBase(object):
    """UI form class for OSM AI dock widget."""
    
    def setupUi(self, QuickOSMAIDockBase):
        QuickOSMAIDockBase.setObjectName("QuickOSMAIDockBase")
        QuickOSMAIDockBase.setMinimumWidth(360)
        QuickOSMAIDockBase.setMaximumWidth(360)
        QuickOSMAIDockBase.setWindowTitle("OSM AI")
        
        # Dock widget contents
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        
        # Root layout
        self.rootLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.rootLayout.setContentsMargins(8, 8, 8, 8)
        self.rootLayout.setSpacing(8)
        self.rootLayout.setObjectName("rootLayout")
        
        # Header frame
        self.headerFrame = QtWidgets.QFrame(self.dockWidgetContents)
        self.headerFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.headerFrame.setObjectName("headerFrame")
        
        self.headerLayout = QtWidgets.QHBoxLayout(self.headerFrame)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(6)
        self.headerLayout.setObjectName("headerLayout")
        
        # Chat tabs
        self.chatTabs = QtWidgets.QTabWidget(self.headerFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.chatTabs.setSizePolicy(sizePolicy)
        self.chatTabs.setMinimumHeight(32)
        self.chatTabs.setMaximumHeight(40)
        self.chatTabs.setTabsClosable(True)
        self.chatTabs.setDocumentMode(True)
        self.chatTabs.setTabPosition(QtWidgets.QTabWidget.North)
        self.chatTabs.setTabBarAutoHide(False)
        self.chatTabs.setObjectName("chatTabs")
        
        self.tabPlaceholder = QtWidgets.QWidget()
        self.tabPlaceholder.setObjectName("tabPlaceholder")
        self.chatTabs.addTab(self.tabPlaceholder, "Chat")
        
        self.headerLayout.addWidget(self.chatTabs)
        
        # New chat button
        self.newChatButton = QtWidgets.QPushButton(self.headerFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.newChatButton.setSizePolicy(sizePolicy)
        self.newChatButton.setMinimumSize(QtCore.QSize(64, 28))
        self.newChatButton.setMaximumSize(QtCore.QSize(90, 28))
        self.newChatButton.setText("")
        self.newChatButton.setObjectName("newChatButton")
        self.headerLayout.addWidget(self.newChatButton)
        
        self.rootLayout.addWidget(self.headerFrame)
        
        # Message scroll area
        self.messageScrollArea = QtWidgets.QScrollArea(self.dockWidgetContents)
        self.messageScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.messageScrollArea.setWidgetResizable(True)
        self.messageScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.messageScrollArea.setObjectName("messageScrollArea")
        
        self.messageContainer = QtWidgets.QWidget()
        self.messageContainer.setObjectName("messageContainer")
        
        self.messageLayout = QtWidgets.QVBoxLayout(self.messageContainer)
        self.messageLayout.setContentsMargins(0, 0, 0, 0)
        self.messageLayout.setSpacing(12)
        self.messageLayout.setAlignment(QtCore.Qt.AlignTop)
        self.messageLayout.setObjectName("messageLayout")
        
        self.messageScrollArea.setWidget(self.messageContainer)
        self.rootLayout.addWidget(self.messageScrollArea)
        
        # Input frame
        self.inputFrame = QtWidgets.QFrame(self.dockWidgetContents)
        self.inputFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inputFrame.setObjectName("inputFrame")
        
        self.inputLayout = QtWidgets.QVBoxLayout(self.inputFrame)
        self.inputLayout.setContentsMargins(0, 0, 0, 0)
        self.inputLayout.setSpacing(6)
        self.inputLayout.setObjectName("inputLayout")
        
        # Mode layout (empty spacers for now)
        self.modeLayout = QtWidgets.QHBoxLayout()
        self.modeLayout.setContentsMargins(0, 0, 0, 0)
        self.modeLayout.setSpacing(6)
        self.modeLayout.setObjectName("modeLayout")
        
        self.modeSpacerLeft = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.modeLayout.addItem(self.modeSpacerLeft)
        
        self.modeSpacerRight = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.modeLayout.addItem(self.modeSpacerRight)
        
        self.inputLayout.addLayout(self.modeLayout)
        
        # Input box
        self.inputBox = QtWidgets.QFrame(self.inputFrame)
        self.inputBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inputBox.setFrameShadow(QtWidgets.QFrame.Plain)
        self.inputBox.setObjectName("inputBox")
        
        self.inputBoxLayout = QtWidgets.QVBoxLayout(self.inputBox)
        self.inputBoxLayout.setContentsMargins(6, 6, 6, 6)
        self.inputBoxLayout.setSpacing(6)
        self.inputBoxLayout.setObjectName("inputBoxLayout")
        
        # Input text edit
        self.inputEdit = QtWidgets.QTextEdit(self.inputBox)
        self.inputEdit.setMinimumHeight(80)
        self.inputEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.inputEdit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.inputEdit.setPlaceholderText("e.g., Get all convenience stores in Shibuya, Tokyo")
        self.inputEdit.setObjectName("inputEdit")
        self.inputBoxLayout.addWidget(self.inputEdit)
        
        # Send layout
        self.sendLayout = QtWidgets.QHBoxLayout()
        self.sendLayout.setContentsMargins(0, 0, 0, 0)
        self.sendLayout.setSpacing(6)
        self.sendLayout.setObjectName("sendLayout")
        
        self.sendSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.sendLayout.addItem(self.sendSpacer)
        
        # Send button
        self.sendButton = QtWidgets.QPushButton(self.inputBox)
        self.sendButton.setMinimumWidth(64)
        self.sendButton.setText("Send")
        self.sendButton.setObjectName("sendButton")
        self.sendLayout.addWidget(self.sendButton)
        
        self.inputBoxLayout.addLayout(self.sendLayout)
        self.inputLayout.addWidget(self.inputBox)
        
        self.rootLayout.addWidget(self.inputFrame)
        
        QuickOSMAIDockBase.setWidget(self.dockWidgetContents)
        
        QtCore.QMetaObject.connectSlotsByName(QuickOSMAIDockBase)
    
    def retranslateUi(self, QuickOSMAIDockBase):
        """Retranslate UI strings (for internationalization)."""
        pass

