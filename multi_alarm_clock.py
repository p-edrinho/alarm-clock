#1 - importar as bibliotecas necessárias
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, LEFT, Toplevel
import datetime
import time
import winsound
import threading
import os

#2 - definir o diretório para o diretório do programa
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#3 - criar a lista global de alarmes para que todos os alarmes de todas as instâncias sejam gerenciados
all_alarms = []

#4 - classe para criar instâncias do relógio despertador
class AlarmClock:
    def __init__(self, master=None, instance_id=1, x_offset=0, y_offset=0):
        self.instance_id = instance_id
        self.alarms = []  # alarmes específicos desta instância
        
        # Criar janela (principal ou secundária)
        if master is None:
            self.clock = Tk()
        else:
            self.clock = Toplevel(master)
        
        self.setup_window(x_offset, y_offset)
        self.setup_interface()
        
    def setup_window(self, x_offset, y_offset):
        """Configurar a janela do alarme"""
        self.clock.title(f"Alarm Clock - Instance {self.instance_id}")
        geometry_str = f"550x450+{346 + x_offset}+{66 + y_offset}"
        self.clock.geometry(geometry_str)
        self.clock.configure(bg="grey")
        
        # Tentar carregar o ícone (opcional)
        try:
            self.clock.iconbitmap(r"C:\Users\pedro\Desktop\pedro\programacao\python\projetos\alarm clock\clock.ico")
        except:
            pass  # Se não encontrar o ícone, continua sem ele
    
    def clear_instruction(self, event):
        """Limpar o texto da caixa de instrução quando focada"""
        if self.instruction_text.get() == "What should i remind you of?":
            self.instruction_text.set("")
    
    def alarm(self, set_alarm_timer, instruction):
        """Funcionalidade do alarme"""
        while True:
            time.sleep(1)
            current_time = datetime.datetime.now()
            now = current_time.strftime("%H:%M:%S")
            if now == set_alarm_timer:
                print(f"Instance {self.instance_id} - Time's up! Reminder: {instruction}")
                try:
                    winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | 0x0000)
                    winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | 0x0000)
                except:
                    # Se não encontrar o arquivo de som, usar beep do sistema
                    winsound.Beep(1000, 1000)
                    winsound.Beep(1000, 1000)
                break
    
    def actual_time(self):
        """Definir o alarme quando o botão é pressionado"""
        h = self.hour.get().replace(" ", "") if self.hour.get().replace(" ", "") else "00"
        m = self.minute.get().replace(" ", "") if self.minute.get().replace(" ", "") else "00"
        s = self.second.get().replace(" ", "") if self.second.get().replace(" ", "") else "00"
        set_alarm_timer = f"{h}:{m}:{s}"
        instruction = self.instruction_text.get()
        
        # Adicionar à lista local e global
        alarm_info = (set_alarm_timer, instruction, self.instance_id)
        self.alarms.append(alarm_info)
        all_alarms.append(alarm_info)
        
        # Iniciar thread do alarme
        threading.Thread(target=self.alarm, args=(set_alarm_timer, instruction), daemon=True).start()
        
        print(f"Alarm set for {set_alarm_timer} on Instance {self.instance_id}: {instruction}")
    
    def update_clock(self):
        """Atualizar o relógio principal em tempo real"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.main_clock.config(text=current_time)
        self.clock.after(1000, self.update_clock)  # Atualizar a cada segundo
    
    def setup_interface(self):
        """Criar a interface gráfica"""
        # Frames principais
        row1 = Frame(self.clock, height=225, width=550)
        row1.pack()
        
        row2 = Frame(self.clock, height=225, width=550)
        row2.pack()
        
        # Colunas
        col1_row1 = Frame(row1, height=225, width=275, bg="lightblue")
        col1_row1.pack(side=LEFT)
        
        col2_row1 = Frame(row1, height=225, width=275, bg="lightgreen")
        col2_row1.pack(side=LEFT)
        
        col1_row2 = Frame(row2, height=225, width=275, bg="lightcoral")
        col1_row2.pack(side=LEFT)
        
        col2_row2 = Frame(row2, height=225, width=275, bg="lightyellow")
        col2_row2.pack(side=LEFT)
        
        # Linhas divisórias
        horizontal_line = Frame(self.clock, height=3, bg="black")
        horizontal_line.place(x=0, y=225, width=550)
        
        vertical_line1 = Frame(self.clock, width=3, bg="black")
        vertical_line1.place(x=275, y=0, height=450)
        
        # Labels
        setYourAlarm = Label(self.clock, text=f"Create alarm - Instance {self.instance_id}", 
                           bg="black", fg="lightblue", font=("helvetica", 13, "bold"))
        setYourAlarm.place(x=80, y=5)
        
        # Relógio principal (será atualizado em tempo real)
        self.main_clock = Label(self.clock, text="00:00:00", font=("helvetica", 25, "bold"), 
                               bg="black", fg="lightblue")
        self.main_clock.place(x=110, y=35)
        
        addTime = Label(self.clock, text="Hour   Minute   Second", bg="black", fg="white", font=60)
        addTime.place(x=93.5, y=87)
        
        time_format = Label(self.clock, text="Enter time in 24-hour format!", fg="red", bg="black", font="Arial")
        time_format.place(x=73.5, y=390)
        
        # Variáveis para entrada
        self.hour = StringVar()
        self.minute = StringVar()
        self.second = StringVar()
        
        # Campos de entrada
        hourTime = Entry(self.clock, textvariable=self.hour, bg="pink", width=3, font=("Arial", 15))
        hourTime.place(x=93.5, y=117)
        
        minuteTime = Entry(self.clock, textvariable=self.minute, bg="pink", width=3, font=("Arial", 15))
        minuteTime.place(x=150, y=117)
        
        secondTime = Entry(self.clock, textvariable=self.second, bg="pink", width=3, font=("Arial", 15))
        secondTime.place(x=209, y=117)
        
        # Botão para criar alarme
        submit = Button(self.clock, text="Set Alarm", bg="black", fg="white", width=10, 
                       command=self.actual_time)
        submit.place(x=135, y=190)
        
        # Caixa de instrução
        self.instruction_text = StringVar(value="What should i remind you of?")
        instruction_entry = Entry(self.clock, textvariable=self.instruction_text, fg="black", 
                                width=24, font=("Arial", 11))
        instruction_entry.place(x=77, y=157)
        instruction_entry.bind("<FocusIn>", self.clear_instruction)
        
        # Iniciar atualização do relógio
        self.update_clock()
    
    def run(self):
        """Iniciar o loop principal"""
        self.clock.mainloop()

#5 - função para criar múltiplas instâncias
def create_multiple_clocks(num_instances=4):
    """Criar múltiplas instâncias do relógio despertador"""
    clocks = []
    
    # Primeira instância (janela principal)
    main_clock = AlarmClock(instance_id=1, x_offset=0, y_offset=0)
    clocks.append(main_clock)
    
    # Instâncias adicionais (janelas secundárias)
    for i in range(2, num_instances + 1):
        # Offset para posicionar as janelas em locais diferentes
        x_offset = (i - 1) * 100
        y_offset = (i - 1) * 50
        
        clock = AlarmClock(master=main_clock.clock, instance_id=i, 
                          x_offset=x_offset, y_offset=y_offset)
        clocks.append(clock)
    
    return clocks

#6 - executar o programa
if __name__ == "__main__":
    # Criar 4 instâncias do relógio
    alarm_clocks = create_multiple_clocks(1)
    
    # Iniciar a primeira instância (que controlará as outras)
    alarm_clocks[0].run()

"""
MELHORIAS IMPLEMENTADAS:
✓ Múltiplas instâncias: Agora você pode ter 4 relógios funcionando simultaneamente
✓ Cada instância tem seu próprio ID e posição na tela
✓ Lista global de alarmes para gerenciar todos os alarmes
✓ Relógio principal atualiza em tempo real
✓ Tratamento de erros para ícone e som
✓ Cores diferentes para cada seção da interface
✓ Cada alarme mostra de qual instância veio

TODO FUTURAS:
- Adicionar botão para deletar alarmes
- Melhorar ainda mais a interface visual
- Adicionar histórico de alarmes
- Permitir configurar quantas instâncias criar
"""