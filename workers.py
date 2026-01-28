import subprocess
import speedtest
from PySide6.QtCore import QThread, Signal

# --- WORKER PARA O PING ---
class PingWorker(QThread):
    finished = Signal(str)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        try:
            # Executa o comando ping do Windows (apenas 1 tentativa para ser rápido)
            output = subprocess.check_output(f"ping -n 1 {self.address}", shell=True, text=True)
            self.finished.emit(f"Sucesso:\n{output}")
        except subprocess.CalledProcessError:
            self.finished.emit(f"Falha: Não foi possível contactar {self.address}")
        except Exception as e:
            self.finished.emit(f"Erro: {str(e)}")

# --- WORKER PARA O SPEEDTEST ---
class SpeedtestWorker(QThread):
    progress = Signal(str) 
    finished = Signal(float, float, float)
    error = Signal(str)

    def run(self):
        try:
            self.progress.emit("A procurar servidor...")
            st = speedtest.Speedtest()
            st.get_best_server()
            
            self.progress.emit("A testar Download...")
            download_bps = st.download()
            download_mbps = download_bps / 1_000_000 # Converter bits para Megabits
            
            self.progress.emit("A testar Upload...")
            upload_bps = st.upload()
            upload_mbps = upload_bps / 1_000_000
            
            ping = st.results.ping
            
            self.finished.emit(download_mbps, upload_mbps, ping)
        except Exception as e:
            self.error.emit(str(e))