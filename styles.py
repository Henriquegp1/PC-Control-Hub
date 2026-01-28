# --- Estilos QSS (CSS para o aplicativo) ---

# Estilo preto
DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: Arial;
        font-size: 14px;
    }
    QPushButton {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #4d4d4d;
    }
    QPushButton:pressed {
        background-color: #555555;
    }
    QFrame#sidebar {
        background-color: #333333;
    }
    QListWidget, QLineEdit, QTextEdit {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px;
    }
    QListWidget::item {
        background-color: transparent;
        padding: 10px 5px; 
        border-bottom: 1px solid #4a4a4a; 
    }
    QLabel#page_title {
        font-size: 20px;
        font-weight: bold;
    }
    QLabel#status_label {
        font-size: 12px;
        color: #888888;
    }
    QToolTip {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
    }
    QLabel#speed_result {
        font-size: 16px;
        color: #4CAF50;
        font-weight: bold;
    }
"""
# Estilo claro
LIGHT_STYLE = """
    QWidget {
        background-color: #f0f0f0;
        color: #000000;
        font-family: Arial;
        font-size: 14px;
    }
    QPushButton {
        background-color: #e1e1e1;
        border: 1px solid #adadad;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #cacaca;
    }
    QPushButton:pressed {
        background-color: #adadad;
    }
    QFrame#sidebar {
        background-color: #dddddd;
    }
    QListWidget, QLineEdit, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #adadad;
        border-radius: 4px;
        padding: 5px;
    }
    QListWidget::item {
        background-color: transparent;
        padding: 10px 5px; 
        border-bottom: 1px solid #dcdcdc; 
    }
    QLabel#page_title {
        font-size: 20px;
        font-weight: bold;
    }
    QLabel#status_label {
        font-size: 12px;
        color: #666666;
    }
    QToolTip {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #adadad;
        padding: 5px;
    }
    QLabel#speed_result {
        font-size: 16px;
        color: #2E7D32;
        font-weight: bold;
    }
"""