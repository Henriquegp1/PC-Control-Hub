🎛️ PC Control Hub

Um painel de controlo centralizado ("All-in-One") para Windows, desenvolvido em Python com uma interface gráfica moderna (PySide6). Este projeto permite gerir, limpar, monitorizar e otimizar o computador a partir de um único local.

🚀 Funcionalidades

O PC Control Hub está organizado em módulos para facilitar a gestão do sistema:

1. 🧹 Limpeza e Otimização

Limpeza de Temporários: Remove ficheiros desnecessários da pasta %TEMP% para libertar espaço.

Esvaziar Reciclagem: Atalho rápido para esvaziar a reciclagem sem confirmações.

Gestor de Arranque (Startup Manager):

Lista todos os programas que iniciam com o Windows.

Ícones Reais: Extrai e exibe o ícone original de cada programa.

Desativar: Permite remover programas do arranque para acelerar o PC.

Backup & Restore: Salva o estado atual do arranque num ficheiro JSON e permite restaurar se necessário.

2. ⚡ Atalhos Rápidos

Acesso imediato a ferramentas essenciais do sistema:

Gestor de Tarefas.

Painel de Controlo (Clássico).

Gestor de Dispositivos.

Desinstalar Aplicações (Programas e Recursos).

3. 📊 Monitorização do Sistema

Painel em tempo real (atualizado a cada segundo) com:

Uso de CPU (%).

Uso de Memória RAM (GB e %).

Ocupação do Disco Principal (C:).

4. 🌐 Rede e Internet

Informações de IP: Mostra o IP Local e o IP Público.

Ping Manual: Ferramenta integrada para testar latência a qualquer site (ex: google.com).

Speedtest: Teste de velocidade de Download, Upload e Ping integrado (usando a rede da Ookla).

5. 🎨 Personalização

Alternância entre Tema Claro e Tema Escuro.

🛠️ Estrutura do Projeto

O código foi organizado de forma modular para facilitar a manutenção:

main.py: O ponto de entrada da aplicação e lógica da interface principal.

workers.py: Contém as "Threads" para tarefas demoradas (Ping, Speedtest) para não travar a janela.

utils.py: Funções utilitárias de sistema (extração de ícones, verificação de administrador).

styles.py: Contém as folhas de estilo (CSS) para os temas Claro e Escuro.

📦 Como Executar (Código Fonte)

Clone o repositório:

git clone [https://github.com/SEU_USUARIO/PC-Control-Hub.git](https://github.com/SEU_USUARIO/PC-Control-Hub.git)
cd PC-Control-Hub


Crie e ative um ambiente virtual (recomendado):

python -m venv .venv
.\.venv\Scripts\Activate


Instale as dependências:

pip install PySide6 psutil requests speedtest-cli


Execute o programa:

python main.py


🔨 Como Criar o Executável (.exe)

Para gerar um ficheiro único e independente que funciona em qualquer PC Windows (sem precisar de Python instalado):

Instale o PyInstaller:

pip install pyinstaller


Execute o comando de construção (certifique-se de ter o icon.ico na pasta):

pyinstaller --noconsole --onefile --name="PC Control Hub" --icon="icon.ico" --add-data "icon.ico;." main.py


O executável final estará na pasta dist.

📝 Licença

Este projeto é de código aberto. Sinta-se à vontade para contribuir, modificar e melhorar!
