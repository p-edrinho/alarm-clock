#1 - importar as bibliotecas necessárias
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import datetime
import time
import threading
import os
import sys
import winsound

#2 - lista global para manter tracking de todas as instancias do alarme
alarm_instances = []

#3 - definir a classe principal e seus metodos
class AlarmClock:
    def __init__(self, is_main=False):
        # define o diretório de trabalho para o diretório do script
        if is_main and getattr(sys, 'frozen', False):
            # se for executado como um .exe
            os.chdir(os.path.dirname(sys.executable))
        elif is_main:
            # se for executado como um script
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # inicia a lista dos alarmes
        self.all_alarms = []
        self.alarm_threads = []
        self.is_main = is_main
        
        # adiciona a instancia em questão à lista
        alarm_instances.append(self)
        
        # cria a janela principal
        self.setup_window()
        
        # cria os elementos da interface
        self.setup_gui()
        
        # inicia o relogio principal
        self.update_main_clock()
    
    # inicia a janela principal do alarme
    def setup_window(self):
        self.clock = tk.Tk()
        self.clock.title(f"Alarm Clock {'(MAIN)' if self.is_main else f'({len(alarm_instances)})'}")
        
        # posiciona as proximas instancias do alarme na tela, de forma que nenhuma se sobreponha
        offset = (len(alarm_instances) - 1) * 30
        self.clock.geometry(f"300x300+{346 + offset}+{66 + offset}")
        self.clock.configure(bg="grey")
        self.clock.resizable(False, False)
        
        # carrega o icone da janela, se nao for encontrado, usa o icone padrão 
        try:
            self.clock.iconbitmap("clock.ico")
        except tk.TclError:
            print("Warning: clock.ico not found, using default icon")
        
        # configura o protocolo de fechamento da janela
        self.clock.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # cria os elementos da interface
    def setup_gui(self):
        # título
        title_label = tk.Label(
            self.clock, 
            text="Create an alarm", 
            bg="black", 
            fg="lightblue", 
            font=("helvetica", 13, "bold")
        )
        title_label.place(x=85, y=5)
        
        # relógio principal
        self.time_now = tk.Label(
            self.clock, 
            text="", 
            font=("helvetica", 25, "bold"), 
            bg="black", 
            fg="lightblue"
        )
        self.time_now.place(x=82, y=35)
        
        # inputs de hora/minuto/segundo
        tk.Label(self.clock, text="Hour", bg="black", fg="white", font=("Arial", 10)).place(x=70.5, y=87)
        tk.Label(self.clock, text="Minute", bg="black", fg="white", font=("Arial", 10)).place(x=120.5, y=87)
        tk.Label(self.clock, text="Second", bg="black", fg="white", font=("Arial", 10)).place(x=180.5, y=87)
        
        # variaveis de hora/minuto/segundo
        self.hour = tk.StringVar()
        self.minute = tk.StringVar()
        self.second = tk.StringVar()
        
        # campos de input de hora/minuto/segundo
        self.hour_entry = tk.Entry(
            self.clock, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.hour_entry.place(x=70.5, y=117)
        
        self.minute_entry = tk.Entry(
            self.clock, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.minute_entry.place(x=127.5, y=117)
        
        self.second_entry = tk.Entry(
            self.clock, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.second_entry.place(x=190.5, y=117)
        
        # input do lembrete do alarme
        self.instruction_entry = tk.Entry(
            self.clock, 
            fg="black", 
            width=18, 
            font=("Arial", 11)
        )
        self.instruction_entry.place(x=76, y=157)
        self.instruction_entry.insert(0, "Reminder:")
        self.instruction_entry.bind("<FocusIn>", self.clear_instruction)
        self.instruction_entry.bind("<FocusOut>", self.set_instruction)
        
        # botao "set alarm" para definir o alarme 
        submit_btn = tk.Button(
            self.clock, 
            text="Set Alarm", 
            bg="black", 
            fg="white", 
            width=10, 
            command=self.set_alarm,
            font=("Arial", 10)
        )
        submit_btn.place(x=105, y=190)
        
        # botoes de + / - com imagens e failproof caso a imagem nao for encontrada (vai criar um botao do tkinter)
        self.create_control_buttons()
        
        # instrução do lembrete
        format_label = tk.Label(
            self.clock, 
            text="Enter time in 24-hour format!", 
            fg="red", 
            bg="black", 
            font=("Arial", 8)
        )
        format_label.place(x=79.5, y=275)
    
    # botoes de + / - com imagens e failproof caso a imagem nao for encontrada (vai criar um botao do tkinter)
    def create_control_buttons(self):
        # carrega as imagens
        plus_img = self.load_resized_image_with_circular_shadow("plus.png", 45, 45)
        minus_img = self.load_resized_image_with_circular_shadow("minus.png", 35, 35)
        
        # guarda as imagens como variaveis da instancia pra garbage collection (memory management)
        self.plus_img = plus_img
        self.minus_img = minus_img
        
        # botao de +
        if plus_img:
            add_btn = tk.Button(
                self.clock, 
                image=plus_img, 
                bg="grey", 
                borderwidth=0, 
                highlightthickness=0, 
                relief="flat", 
                activebackground="grey",
                command=self.add_new_alarm_window
            )
        else:
            add_btn = tk.Button(
                self.clock, 
                text="+", 
                bg="white", 
                fg="black", 
                width=3, 
                height=1, 
                font=("Arial", 15),
                command=self.add_new_alarm_window
            )
        add_btn.place(x=124.5, y=220)
        
        # botao de -
        if minus_img:
            remove_btn = tk.Button(
                self.clock, 
                image=minus_img, 
                bg="grey", 
                borderwidth=0, 
                highlightthickness=0, 
                relief="flat", 
                activebackground="grey",
                command=self.remove_current_window
            )
        else:
            remove_btn = tk.Button(
                self.clock, 
                text="-", 
                bg="white", 
                fg="black", 
                width=3, 
                height=1, 
                font=("Arial", 15),
                command=self.remove_current_window
            )
        remove_btn.place(x=250, y=250)
        
        # guarda os botoes como variaveis da instancia pra garbage collection
        self.add_btn = add_btn
        self.remove_btn = remove_btn
    
    # metódo para criar uma nova janela do alarme e printa o total de instancias
    def add_new_alarm_window(self):
        try:
            _new_alarm = AlarmClock(is_main=False)
            print(f"Created new alarm window. Total windows: {len(alarm_instances)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new alarm window: {str(e)}")
    
    # metodo para fechar a janela atual
    def remove_current_window(self):
        try:
            # pergunta se realmente deseja fechar a janela e printa caso aconteça algum erro
            if messagebox.askyesno("Confirm", "Close this alarm window?", parent=self.clock):
                self.close_window()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to close window: {str(e)}", parent=self.clock)
    
    # metodo para fechar a janela e limpar a memoria
    def close_window(self):
        try:
            # remove da lista global de instancias do alarme
            if self in alarm_instances:
                alarm_instances.remove(self)
            
            # para todos os alarmes dessa instancia
            for thread in self.alarm_threads:
                pass
            
            # fecha a janela e printa as janelas restantes e printa caso aconteca algum erro
            self.clock.destroy()
            
            print(f"Window closed. Remaining windows: {len(alarm_instances)}")
            
        except Exception as e:
            print(f"Error closing window: {e}")
    
    # formas de validaçao do input de hora (0-23) sem limpar o campo
    def validate_hour_input(self, value):
        if value == "":
            return True  # permite campo vazio
        if not value.isdigit():
            return False  # nao permite caracteres nao numericos
        if len(value) > 2:
            return False  # maximo de 2 digitos
        num = int(value)
        return 0 <= num <= 23  # o range valido pra hora
    
    # mesma coisa da hora, so que para os minutos e segundos
    def validate_minute_second_input(self, value):
        if value == "":
            return True  # permite campo vazio
        if not value.isdigit():
            return False  # nao permite caracteres nao numericos
        if len(value) > 2:
            return False  # maximo de 2 digitos
        num = int(value)
        return 0 <= num <= 59  # range valido pra minutos/segundos

    # metodo responsavel por dar resize na imagem com um efeito de sombra circular
    def load_resized_image_with_circular_shadow(self, image_path, max_width, max_height):
        try:
            # checa se o arquivo da imagem existe
            if not os.path.exists(image_path):
                print(f"Image file {image_path} not found")
                return None
                
            # carrega e da resize na imagem
            image = Image.open(image_path).convert("RGBA")
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # cria uma "imagem" maior para o efeito de sombra
            shadow_offset = 3
            canvas_size = (max_width + shadow_offset * 2, max_height + shadow_offset * 2)
            canvas = Image.new('RGBA', canvas_size, (128, 128, 128, 0))
            
            # faz a sombra ser circular
            shadow_size = min(image.size)
            shadow_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            
            # "desenha" a sombra circular
            shadow_pos = (shadow_offset + 2, shadow_offset + 2)
            shadow_end = (shadow_pos[0] + shadow_size, shadow_pos[1] + shadow_size)
            shadow_draw.ellipse([shadow_pos, shadow_end], fill=(0, 0, 0, 60))
            
            # da uma borrada na sombra
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(2))
            
            # 
            canvas = Image.alpha_composite(canvas.convert('RGBA'), shadow_img)
            image_pos = (shadow_offset, shadow_offset)
            canvas.paste(image, image_pos, image)
            
            # cria a imagem final e retorna pra janela em questao como main
            return ImageTk.PhotoImage(canvas, master=self.clock)
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None
    
    # metodo para limpar/recolocar o campo de instrucoes
    def clear_instruction(self, event):
        current_text = self.instruction_entry.get()
        if current_text == "Reminder:":
            self.instruction_entry.delete(0, tk.END)
    
    def set_instruction(self, event):
        current_text = self.instruction_entry.get().strip()
        if current_text == "":
            self.instruction_entry.delete(0, tk.END)
            self.instruction_entry.insert(0, "Reminder:")

    # atualiza o relogio principal a cada segundo, se a janela em questao for destruida, para de atualizar
    def update_main_clock(self):
        try:
            current_time = datetime.datetime.now()
            now = current_time.strftime("%H:%M:%S")
            self.time_now.config(text=now)
            self.clock.after(1000, self.update_main_clock)
        except tk.TclError:
            pass
    
    # define um novo alarme obs.: le os valores diretamente da widget
    def set_alarm(self):
        try:
            h = self.hour_entry.get().replace(" ", "")
            m = self.minute_entry.get().replace(" ", "")
            s = self.second_entry.get().replace(" ", "")
            instruction_input = self.instruction_entry.get().strip()
            
            # converte os valores vazios para "0"
            h = h if h else "0"
            m = m if m else "0"
            s = s if s else "0"
            
            # se o campo de instrucao estiver vazio, usa a mensagem padrao
            instruction = instruction_input if instruction_input and instruction_input != "Reminder:" else "Time's up!"
            
            # valida os inputs para que todos sejam apenas numeros
            if not (h.isdigit() and m.isdigit() and s.isdigit()):
                messagebox.showerror("Invalid Input", "Please enter only numbers for time!", parent=self.clock)
                return
            
            # converte para int e verifica os ranges
            hour_int = int(h)
            minute_int = int(m)
            second_int = int(s)
            
            if not (0 <= hour_int <= 23):
                messagebox.showerror("Invalid Hour", "Hour must be between 0 and 23!", parent=self.clock)
                return
            if not (0 <= minute_int <= 59):
                messagebox.showerror("Invalid Minute", "Minute must be between 0 and 59!", parent=self.clock)
                return
            if not (0 <= second_int <= 59):
                messagebox.showerror("Invalid Second", "Second must be between 0 and 59!", parent=self.clock)
                return
            
            # formataçao com 2 zeros
            h = f"{hour_int:02d}"
            m = f"{minute_int:02d}"
            s = f"{second_int:02d}"
            
            set_alarm_timer = f"{h}:{m}:{s}"
            
            # adiciona o alarme à lista
            alarm_info = {
                'time': set_alarm_timer,
                'instruction': instruction,
                'active': True
            }
            self.all_alarms.append(alarm_info)
            
            # inicia a thread do alarme
            alarm_thread = threading.Thread(
                target=self.alarm_worker, 
                args=(set_alarm_timer, instruction, self.clock), 
                daemon=True
            )
            alarm_thread.start()
            self.alarm_threads.append(alarm_thread)
            
            messagebox.showinfo("Alarm Set", f"Alarm set for {set_alarm_timer}\nReminder: {instruction}", parent=self.clock)
            
            # limpa os inputs
            self.hour_entry.delete(0, tk.END)
            self.minute_entry.delete(0, tk.END)
            self.second_entry.delete(0, tk.END)
            self.instruction_entry.delete(0, tk.END)
            self.instruction_entry.insert(0, "Reminder:")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set alarm: {str(e)}")
    
    # metodo para monitorar o alarme
    def alarm_worker(self, set_alarm_timer, instruction, parent_window):
        try:
            while True:
                time.sleep(1)
                current_time = datetime.datetime.now()
                now = current_time.strftime("%H:%M:%S")
                
                if now == set_alarm_timer:
                    print(f"Time's up! Reminder: {instruction}")
                    self.play_alarm_sound()
                    
                    # mostra a notificaçao do alarme e ignora se a janela tiver sido fechada
                    try:
                        parent_window.after(0, lambda: messagebox.showinfo("Alarm!", f"Time's up!\nReminder: {instruction}", parent=parent_window))
                    except tk.TclError:
                        pass
                    break
        except Exception as e:
            print(f"Alarm error: {e}")
    
    # metodo para tocar o som do alarme, com fallback pra caso o som nao seja encontrado/carregado (nesse caso, toca um beep)
    def play_alarm_sound(self):
        try:
            if os.path.exists("vineboom.wav"):
                winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | winsound.SND_NOWAIT)
                winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | winsound.SND_NOWAIT)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            print(f"Error playing alarm sound: {e}")
    
    # metodo para fechar a janela
    def on_closing(self):
        if len(alarm_instances) <= 1:
            # se for a ultima janela, pede confirmaçao para fechar todo o programa
            if messagebox.askokcancel("Quit", "Do you want to quit the application?", parent=self.clock):
                # fecha todas as janelas restantes
                for instance in alarm_instances[:]:
                    try:
                        instance.clock.destroy()
                    except tk.TclError:
                        pass
                    except Exception as e:
                        print(f"Error closing window: {e}")
                alarm_instances.clear()
        else:
            # se nao for a ultima janela, pede confirmaçao para fechar a janela
            if messagebox.askyesno("Close Window", "Close this alarm window?"):
                self.close_window()
    
    # inicia a aplicaçao
    def run(self):
        self.clock.mainloop()

# cria e roda a aplicação
if __name__ == "__main__":
    main_app = AlarmClock(is_main=True)
    main_app.run()

# TODO: adicionar uma forma de escolher seu proprio som pro alarme --?
# TODO: melhorar a gui pra ser mais agradavel visualmente --?
# TODO: fazer a notificaçao do alarme ser menos intrusiva
# TODO: lista de todos os alarmes atuais
# TODO: mostrar visualmente qual eh a main window, e fazer com que, ao ela ser fechada, feche todas as outras janelas e seus respectivos alarmes/processos