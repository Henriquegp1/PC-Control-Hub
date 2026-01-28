"""
PC Control Hub - main.py

Este ficheiro contém a janela principal da aplicação, criação de páginas
e lógica de interação. Os workers e estilos ficam em módulos separados
(`workers.py`, `styles.py`, `utils.py`).
"""

import ctypes
import os
import sys
import subprocess
import shutil
import glob
import psutil
import winreg
import json
import socket
import requests

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QListWidget, QListWidgetItem, QStyle,
    QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt, QTimer

# --- IMPORTAÇÕES DOS NOSSOS MÓDULOS ---
from styles import DARK_STYLE, LIGHT_STYLE
from workers import PingWorker, SpeedtestWorker
from utils import resource_path, is_admin, get_icon_for_executable

try:
    myappid = 'pccontrolhub.app.v3.0' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


# --- MainWindow: janela principal, layouts e comportamentos das páginas ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Control Hub")
        self.setGeometry(100, 100, 900, 650)
        self.current_startup_programs = [] 

        # Tenta carregar um ícone personalizado se existir
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_limpeza = QPushButton("Limpeza")
        btn_limpeza.setToolTip("Ferramentas para limpar arquivos e gerir arranque")

        btn_atalhos = QPushButton("Atalhos")
        btn_atalhos.setToolTip("Acesso rápido a ferramentas do Windows")

        btn_monitor = QPushButton("Monitor")
        btn_monitor.setToolTip("Ver uso de CPU, RAM e Disco")

        btn_rede = QPushButton("Rede")
        btn_rede.setToolTip("Informações de IP, Ping e Teste de Velocidade")

        btn_config = QPushButton("Configurações")
        btn_config.setToolTip("Alterar tema do aplicativo")

        sidebar_layout.addWidget(btn_limpeza)
        sidebar_layout.addWidget(btn_atalhos)
        sidebar_layout.addWidget(btn_monitor)
        sidebar_layout.addWidget(btn_rede)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_config)
        
        self.pages_widget = QStackedWidget()

        self.page_limpeza = self.create_limpeza_page()
        self.page_atalhos = self.create_atalhos_page()
        self.page_monitor = self.create_monitor_page()
        self.page_rede = self.create_rede_page()
        self.page_config = self.create_config_page()

        self.pages_widget.addWidget(self.page_limpeza)
        self.pages_widget.addWidget(self.page_atalhos)
        self.pages_widget.addWidget(self.page_monitor)
        self.pages_widget.addWidget(self.page_rede)
        self.pages_widget.addWidget(self.page_config)

        btn_limpeza.clicked.connect(lambda: self.pages_widget.setCurrentIndex(0))
        btn_atalhos.clicked.connect(lambda: self.pages_widget.setCurrentIndex(1))
        btn_monitor.clicked.connect(lambda: self.pages_widget.setCurrentIndex(2))
        btn_rede.clicked.connect(lambda: self.pages_widget.setCurrentIndex(3))
        btn_config.clicked.connect(lambda: self.pages_widget.setCurrentIndex(4))

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.pages_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.set_theme('dark')

        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_system_info)
        self.monitor_timer.start(1000) 

    # --- Backend: Operações do sistema (limpeza, arranque, utilitários) ---
    # Responsabilidades deste bloco:
    # - Executar ações do sistema (abrir Painel de Controlo, Gestor de Tarefas)
    # - Limpeza de ficheiros temporários e reciclagem
    # - Gerir programas de arranque (backup/restore/disable)
    
    def open_task_manager(self):
        try:
            subprocess.Popen('taskmgr.exe')
            self.status_label_atalhos.setText("Gestor de Tarefas iniciado.")
        except Exception as e:
            self.status_label_atalhos.setText(f"Erro ao abrir Gestor: {e}")

    def open_control_panel(self):
        try:
            subprocess.Popen('control.exe')
            self.status_label_atalhos.setText("Painel de Controlo iniciado.")
        except Exception as e:
            self.status_label_atalhos.setText(f"Erro ao abrir Painel de Controlo: {e}")

    def open_device_manager(self):
        try:
            subprocess.Popen('devmgmt.msc', shell=True)
            self.status_label_atalhos.setText("Gestor de Dispositivos iniciado.")
        except Exception as e:
            self.status_label_atalhos.setText(f"Erro ao abrir Gestor de Dispositivos: {e}")

    def open_programs_and_features(self):
        try:
            subprocess.Popen('appwiz.cpl', shell=True)
            self.status_label_atalhos.setText("Programas e Recursos iniciado.")
        except Exception as e:
            self.status_label_atalhos.setText(f"Erro ao abrir Programas e Recursos: {e}")

    def clean_temp_files(self):
        self.status_label_limpeza.setText("A procurar ficheiros temporários...")
        QApplication.processEvents()
        
        temp_folder = os.environ.get('TEMP')
        if not temp_folder:
            self.status_label_limpeza.setText("Erro: Não foi possível encontrar a pasta TEMP.")
            return

        self.status_label_limpeza.setText(f"Limpando pasta: {temp_folder}...")
        QApplication.processEvents()

        deleted_count = 0
        error_count = 0

        for path in glob.glob(os.path.join(temp_folder, '*')) + glob.glob(os.path.join(temp_folder, '.*')):
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                error_count += 1
        
        self.status_label_limpeza.setText(f"Limpeza concluída! {deleted_count} itens removidos. {error_count} erros.")

    def empty_recycle_bin(self):
        self.status_label_limpeza.setText("A esvaziar a Reciclagem...")
        QApplication.processEvents()
        try:
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            if result == 0:
                self.status_label_limpeza.setText("Reciclagem esvaziada com sucesso!")
            else:
                self.status_label_limpeza.setText(f"Não foi possível esvaziar a Reciclagem (código: {result}).")
        except Exception as e:
            self.status_label_limpeza.setText(f"Erro ao esvaziar a Reciclagem: {e}")

    def get_startup_programs(self):
        startup_programs = []
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]

        for hive, path in registry_paths:
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            program_details = {"name": name, "command": value, "hive": hive, "path": path}
                            startup_programs.append(program_details)
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
        return startup_programs

    def populate_startup_list(self):
        self.startup_list_widget.clear()
        self.current_startup_programs = self.get_startup_programs()
        
        if self.current_startup_programs:
            for program in self.current_startup_programs:
                list_item = QListWidgetItem(self.startup_list_widget)
                item_widget = QWidget()
                item_widget.setMinimumHeight(40)

                item_layout = QHBoxLayout(item_widget)
                item_layout.setSpacing(10) 
                item_layout.setContentsMargins(5, 2, 5, 2)
                
                icon_label = QLabel()
                icon_label.setFixedSize(32, 32)
                
                # --- AQUI: Usa a função importada de utils.py ---
                pixmap = get_icon_for_executable(program["command"])
                if pixmap:
                    icon_label.setPixmap(pixmap)
                else:
                    default_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
                    icon_label.setPixmap(default_icon.pixmap(32, 32))

                name_label = QLabel(program["name"])
                name_label.setWordWrap(True)

                disable_button = QPushButton("Desativar")
                disable_button.setFixedWidth(90)
                disable_button.setToolTip(f"Desativar {program['name']} do arranque do Windows")
                disable_button.clicked.connect(lambda checked, p=program: self.disable_startup_program(p))

                item_layout.addWidget(icon_label)
                item_layout.addWidget(name_label)
                item_layout.addStretch()
                item_layout.addWidget(disable_button)
                
                list_item.setSizeHint(item_widget.sizeHint())
                self.startup_list_widget.addItem(list_item)
                self.startup_list_widget.setItemWidget(list_item, item_widget)

            self.btn_backup_startup.setEnabled(True)
        else:
            self.startup_list_widget.addItem("Nenhum programa de arranque encontrado.")
            self.btn_backup_startup.setEnabled(False)

        self.status_label_limpeza.setText(f"{len(self.current_startup_programs)} programas de arranque encontrados.")
        
        if os.path.exists("startup_backup.json"):
            self.btn_restore_startup.setEnabled(True)
        else:
            self.btn_restore_startup.setEnabled(False)

    def backup_startup_state(self):
        backup_file = "startup_backup.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.current_startup_programs, f, indent=4)
            self.status_label_limpeza.setText(f"Backup salvo com sucesso em {backup_file}!")
            self.btn_restore_startup.setEnabled(True)
        except Exception as e:
            self.status_label_limpeza.setText(f"Erro ao salvar backup: {e}")

    def restore_startup_state(self):
        backup_file = "startup_backup.json"
        try:
            with open(backup_file, 'r') as f:
                backup_programs = json.load(f)
        except FileNotFoundError:
            self.status_label_limpeza.setText("Ficheiro de backup não encontrado! Crie um primeiro.")
            return
        except Exception as e:
            self.status_label_limpeza.setText(f"Erro ao ler o backup: {e}")
            return

        restored_count = 0
        error_count = 0
        for program in backup_programs:
            try:
                hive, path, name, command = program["hive"], program["path"], program["name"], program["command"]
                with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                restored_count += 1
            except Exception as e:
                error_count += 1

        self.status_label_limpeza.setText(f"Restauro concluído! {restored_count} programas restaurados. {error_count} erros.")
        self.populate_startup_list()

    def disable_startup_program(self, program_details):
        try:
            hive, path, name = program_details["hive"], program_details["path"], program_details["name"]
            with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
            self.status_label_limpeza.setText(f'Programa "{name}" desativado com sucesso!')
            self.populate_startup_list()
        except FileNotFoundError:
             self.status_label_limpeza.setText(f'Erro: O programa "{name}" já não existe no registo.')
        except Exception as e:
            self.status_label_limpeza.setText(f"Erro ao desativar: {e}")

    def update_system_info(self):
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_label.setText(f"Uso de CPU: {cpu_percent}%")

        ram = psutil.virtual_memory()
        ram_total_gb, ram_used_gb = ram.total / (1024**3), ram.used / (1024**3)
        self.ram_label.setText(f"Uso de RAM: {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB ({ram.percent}%)")

        try:
            disk = psutil.disk_usage('C:')
            disk_total_gb, disk_used_gb = disk.total / (1024**3), disk.used / (1024**3)
            self.disk_label.setText(f"Uso de Disco (C:): {disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB ({disk.percent}%)")
        except FileNotFoundError:
            self.disk_label.setText("Uso de Disco (C:): Unidade não encontrada.")

    # --- Rede: IP, Ping e Speedtest (network utilities) ---
    # - `get_ip_info`: obtém IP local e público
    # - `start_ping_test` / `handle_ping_result`: ping via worker
    # - `start_speedtest` / handlers: Speedtest via worker (Ookla)
    def get_ip_info(self):
        self.status_label_rede.setText("A obter informações de IP...")
        QApplication.processEvents()
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            try:
                public_ip = requests.get('https://api.ipify.org').text
            except:
                public_ip = "Sem internet"
            self.label_local_ip.setText(f"IP Local: {local_ip}")
            self.label_public_ip.setText(f"IP Público: {public_ip}")
            self.status_label_rede.setText("Informações de IP atualizadas.")
        except Exception as e:
            self.status_label_rede.setText(f"Erro ao obter IPs: {e}")

    def start_ping_test(self):
        address = self.input_ping.text()
        if not address:
            self.status_label_rede.setText("Por favor, digite um endereço para testar.")
            return
        self.status_label_rede.setText(f"A testar ping para {address}...")
        self.text_ping_result.clear()
        
        # --- USA O WORKER IMPORTADO ---
        self.ping_worker = PingWorker(address)
        self.ping_worker.finished.connect(self.handle_ping_result)
        self.ping_worker.start()

    def handle_ping_result(self, result):
        self.text_ping_result.setText(result)
        self.status_label_rede.setText("Teste de Ping concluído.")

    def start_speedtest(self):
        self.status_label_rede.setText("A preparar Teste de Velocidade...")
        self.btn_speedtest.setEnabled(False) 
        
        # --- USA O WORKER IMPORTADO ---
        self.speed_worker = SpeedtestWorker()
        self.speed_worker.progress.connect(self.update_speed_status)
        self.speed_worker.finished.connect(self.handle_speedtest_result)
        self.speed_worker.error.connect(self.handle_speedtest_error)
        self.speed_worker.start()

    def update_speed_status(self, msg):
        self.status_label_rede.setText(msg)

    def handle_speedtest_result(self, down, up, ping):
        self.label_speed_down.setText(f"Download: {down:.2f} Mbps")
        self.label_speed_up.setText(f"Upload: {up:.2f} Mbps")
        self.label_speed_ping.setText(f"Ping: {ping:.0f} ms")
        self.status_label_rede.setText("Teste de Velocidade concluído!")
        self.btn_speedtest.setEnabled(True)

    def handle_speedtest_error(self, err):
        self.status_label_rede.setText(f"Erro no Speedtest: {err}")
        self.btn_speedtest.setEnabled(True)

    # --- UI: Página - Limpeza e Otimização ---
    # Contém ações de limpeza, gestão de arranque e botões relacionados.
    def create_limpeza_page(self):
        page = self.create_page("Limpeza e Otimização")
        layout = page.layout()
        btn_clean_temp = QPushButton("Limpar Ficheiros Temporários")
        btn_clean_temp.setToolTip("Apaga ficheiros temporários do sistema para libertar espaço.")
        btn_clean_temp.clicked.connect(self.clean_temp_files)
        layout.addWidget(btn_clean_temp)
        btn_empty_recycle_bin = QPushButton("Esvaziar Reciclagem")
        btn_empty_recycle_bin.setToolTip("Esvazia a Reciclagem do Windows permanentemente.")
        btn_empty_recycle_bin.clicked.connect(self.empty_recycle_bin)
        layout.addWidget(btn_empty_recycle_bin)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        startup_label = QLabel("Gestor de Programas de Arranque")
        startup_label.setObjectName("page_title")
        layout.addWidget(startup_label)
        self.startup_list_widget = QListWidget()
        layout.addWidget(self.startup_list_widget)
        startup_buttons_layout = QHBoxLayout()
        btn_scan_startup = QPushButton("Analisar")
        btn_scan_startup.setToolTip("Procurar programas que iniciam com o Windows.")
        btn_scan_startup.clicked.connect(self.populate_startup_list)
        self.btn_backup_startup = QPushButton("Salvar Estado")
        self.btn_backup_startup.setToolTip("Cria um backup da lista atual para restauro futuro.")
        self.btn_backup_startup.clicked.connect(self.backup_startup_state)
        self.btn_backup_startup.setEnabled(False) 
        self.btn_restore_startup = QPushButton("Carregar Estado")
        self.btn_restore_startup.setToolTip("Restaura os programas de arranque a partir do backup.")
        self.btn_restore_startup.clicked.connect(self.restore_startup_state)
        self.btn_restore_startup.setEnabled(False)
        startup_buttons_layout.addWidget(btn_scan_startup)
        startup_buttons_layout.addWidget(self.btn_backup_startup)
        startup_buttons_layout.addWidget(self.btn_restore_startup)
        layout.addLayout(startup_buttons_layout)
        self.status_label_limpeza = QLabel("Aguardando comando...")
        self.status_label_limpeza.setObjectName("status_label")
        layout.addWidget(self.status_label_limpeza)
        return page

    def create_atalhos_page(self):
        page = self.create_page("Atalhos Rápidos do Sistema")
        layout = page.layout()
        btn_task_manager = QPushButton("Abrir Gestor de Tarefas")
        btn_task_manager.setToolTip("Abre o Gestor de Tarefas do Windows.")
        btn_task_manager.clicked.connect(self.open_task_manager)
        layout.addWidget(btn_task_manager)
        btn_control_panel = QPushButton("Abrir Painel de Controlo")
        btn_control_panel.setToolTip("Abre o Painel de Controlo clássico.")
        btn_control_panel.clicked.connect(self.open_control_panel)
        layout.addWidget(btn_control_panel)
        btn_device_manager = QPushButton("Abrir Gestor de Dispositivos")
        btn_device_manager.setToolTip("Ver e gerir hardware e drivers.")
        btn_device_manager.clicked.connect(self.open_device_manager)
        layout.addWidget(btn_device_manager)
        btn_programs_features = QPushButton("Desinstalar Aplicações")
        btn_programs_features.setToolTip("Abrir janela para remover programas instalados.")
        btn_programs_features.clicked.connect(self.open_programs_and_features)
        layout.addWidget(btn_programs_features)
        self.status_label_atalhos = QLabel("")
        self.status_label_atalhos.setObjectName("status_label")
        layout.addWidget(self.status_label_atalhos)
        return page
    
    def create_monitor_page(self):
        page = self.create_page("Monitor do Sistema em Tempo Real")
        layout = page.layout()
        self.cpu_label = QLabel("Uso de CPU: --%")
        self.cpu_label.setObjectName("status_label")
        self.cpu_label.setStyleSheet("font-size: 18px;")
        self.cpu_label.setToolTip("Percentagem de processamento em uso.")
        layout.addWidget(self.cpu_label)
        self.ram_label = QLabel("Uso de RAM: -- GB / -- GB (--%)")
        self.ram_label.setObjectName("status_label")
        self.ram_label.setStyleSheet("font-size: 18px;")
        self.ram_label.setToolTip("Memória física usada vs total disponível.")
        layout.addWidget(self.ram_label)
        self.disk_label = QLabel("Uso de Disco (C:): -- GB / -- GB (--%)")
        self.disk_label.setObjectName("status_label")
        self.disk_label.setStyleSheet("font-size: 18px;")
        self.disk_label.setToolTip("Espaço usado no disco principal.")
        layout.addWidget(self.disk_label)
        return page

    # --- UI: Página - Rede e Internet ---
    # Mostra IPs, permite ping manual e executa Speedtest.
    def create_rede_page(self):
        page = self.create_page("Rede e Internet")
        layout = page.layout()
        ip_frame = QFrame()
        ip_layout = QVBoxLayout(ip_frame)
        ip_layout.setContentsMargins(0,0,0,0) 
        
        self.label_local_ip = QLabel("IP Local: --")
        self.label_local_ip.setStyleSheet("font-size: 16px;")
        self.label_public_ip = QLabel("IP Público: --")
        self.label_public_ip.setStyleSheet("font-size: 16px;")
        
        btn_get_ip = QPushButton("Verificar IPs")
        btn_get_ip.clicked.connect(self.get_ip_info)
        
        ip_layout.addWidget(self.label_local_ip)
        ip_layout.addWidget(self.label_public_ip)
        ip_layout.addWidget(btn_get_ip)
        layout.addWidget(ip_frame)
        
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        
        layout.addWidget(separator1)
        speed_label = QLabel("Teste de Velocidade (Speedtest)")
        speed_label.setObjectName("page_title")
        layout.addWidget(speed_label)
        results_layout = QHBoxLayout()
        self.label_speed_down = QLabel("Download: -- Mbps")
        self.label_speed_down.setObjectName("speed_result")
        self.label_speed_up = QLabel("Upload: -- Mbps")
        self.label_speed_up.setObjectName("speed_result")
        self.label_speed_ping = QLabel("Ping: -- ms")
        self.label_speed_ping.setObjectName("speed_result")
        results_layout.addWidget(self.label_speed_down)
        results_layout.addWidget(self.label_speed_up)
        results_layout.addWidget(self.label_speed_ping)
        layout.addLayout(results_layout)
        self.btn_speedtest = QPushButton("Iniciar Speedtest")
        self.btn_speedtest.clicked.connect(self.start_speedtest)
        layout.addWidget(self.btn_speedtest)
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        ping_label = QLabel("Ping Manual (CMD)")
        ping_label.setObjectName("page_title")
        layout.addWidget(ping_label)
        self.input_ping = QLineEdit()
        self.input_ping.setPlaceholderText("Digite um site (ex: google.com)")
        layout.addWidget(self.input_ping)
        btn_ping = QPushButton("Testar Ping")
        btn_ping.clicked.connect(self.start_ping_test)
        layout.addWidget(btn_ping)
        self.text_ping_result = QTextEdit()
        self.text_ping_result.setReadOnly(True)
        self.text_ping_result.setPlaceholderText("O resultado do ping aparecerá aqui...")
        layout.addWidget(self.text_ping_result)
        self.status_label_rede = QLabel("Aguardando comando...")
        self.status_label_rede.setObjectName("status_label")
        layout.addWidget(self.status_label_rede)
        return page

    def create_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label = QLabel(title)
        label.setObjectName("page_title")
        layout.addWidget(label)
        return page

    # --- UI: Página - Configurações ---
    # Troca de temas e preferências da aplicação.
    def create_config_page(self):
        page = self.create_page("Configurações do Aplicativo")
        layout = page.layout()
        theme_label = QLabel("Escolha o tema da aplicação:")
        btn_light_mode = QPushButton("Modo Claro")
        btn_dark_mode = QPushButton("Modo Escuro")
        btn_light_mode.clicked.connect(lambda: self.set_theme('light'))
        btn_dark_mode.clicked.connect(lambda: self.set_theme('dark'))
        btn_light_mode.setToolTip("Mudar para tema claro.")
        btn_dark_mode.setToolTip("Mudar para tema escuro.")
        layout.addWidget(theme_label)
        layout.addWidget(btn_light_mode)
        layout.addWidget(btn_dark_mode)
        return page

    # --- Helpers de UI ---
    # Funções de apoio à interface, como alteração de tema.
    def set_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

if __name__ == "__main__":
    if is_admin():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)