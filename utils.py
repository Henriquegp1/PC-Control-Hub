import sys
import os
import ctypes
import re
from PySide6.QtGui import QImage, QPixmap

class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ("hIcon", ctypes.c_void_p),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", ctypes.c_uint),
        ("szDisplayName", ctypes.c_wchar * 260),
        ("szTypeName", ctypes.c_wchar * 80),
    ]

# Esta função encontra o ícone quer esteja na pasta, quer esteja "dentro" do .exe
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- FUNÇÕES DE ÍCONES ---

def get_icon_for_executable(command):
    main_exe_path = _get_main_executable_path(command)
    
    if not main_exe_path:
        return None

    if 'update.exe' in main_exe_path.lower():
        match = re.search(r'\s([\w-]+\.exe)', command)
        if match:
            secondary_exe_name = match.group(1)
            base_dir = os.path.dirname(main_exe_path)
            search_dirs = [base_dir, os.path.abspath(os.path.join(base_dir, '..'))]
            
            for s_dir in search_dirs:
                for root, _, files in os.walk(s_dir):
                    if secondary_exe_name.lower() in [f.lower() for f in files]:
                        found_path = os.path.join(root, secondary_exe_name)
                        pixmap = _extract_pixmap_from_path(found_path)
                        if pixmap:
                            return pixmap
    
    return _extract_pixmap_from_path(main_exe_path)

def _get_main_executable_path(command):
    command = command.strip()
    if command.startswith('"'):
        end_quote = command.find('"', 1)
        if end_quote != -1:
            return command[1:end_quote]
    
    parts = command.split()
    path_candidate = ""
    for part in parts:
        path_candidate += part + " "
        if path_candidate.lower().strip().endswith('.exe'):
            return path_candidate.strip()
    return None

def _extract_pixmap_from_path(file_path):
    if not os.path.exists(file_path):
        return None

    SHGFI_ICON = 0x000000100
    SHGFI_SMALLICON = 0x000000001
    
    file_info = SHFILEINFO()
    flags = SHGFI_ICON | SHGFI_SMALLICON
    
    try:
        ctypes.windll.shell32.SHGetFileInfoW(
            ctypes.c_wchar_p(file_path), 0, ctypes.byref(file_info), ctypes.sizeof(file_info), flags
        )
        
        hicon = file_info.hIcon
        if hicon:
            image = QImage.fromHICON(hicon)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                ctypes.windll.user32.DestroyIcon(hicon)
                return pixmap
    except Exception:
        return None
    return None