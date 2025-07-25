#1 - importar as bibliotecas necessárias
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, LEFT
import datetime
import time
import winsound
import threading
import os

#2 - definir o diretório para o diretório do programa
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#3 - criar a lista de alarmes para que mais de 1 alarme possa existir por vez
alarms = []

#4 - definir as funções que serão usadas
# a função a seguir serve para limpar o texto da caixa de instrução quando ela for focalizada (clicada)
def clear_instruction(event):
    if instruction_text.get() == "What should i remind you of?":
        instruction_text.set("")

# a função a seguir define a funcionalidade do alarme
# verifica a hora atual, e a cada segundo compara com o input do usuario
# winsound.PlaySound é usado para tocar o som do alarme, toca 2x e sem dar overlap
def alarm(set_alarm_timer, instruction):
    while True:
        time.sleep(1)
        current_time = datetime.datetime.now()
        now = current_time.strftime("%H:%M:%S")
        if now == set_alarm_timer:
            print(f"Time's up! Reminder: {instruction}")
            winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | 0x0000)
            winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | 0x0000)
            break

# a função a seguir define o que acontece quando o botão "Set Alarm" é pressionado
# hour.get pega o valor inserido na hora, .replace(" ", "") transforma todos os espaços em branco em algo vazio e,
# checa se: o numero for de fato algo, retorna esse valor, do contrario retorna "00"
# mesma coisa para minute.get e second.get
# alarms.append faz com que o alarme seja adicionado à lista de alarmes
# threading.Thread é usado para criar uma nova thread para o alarme, permitindo que o programa continue rodando enquanto o alarme espera
def actual_time():
    h = hour.get().replace(" ", "") if hour.get().replace(" ", "") else "00"
    m = minute.get().replace(" ", "") if minute.get().replace(" ", "") else "00"
    s = second.get().replace(" ", "") if second.get().replace(" ", "") else "00"
    set_alarm_timer = f"{h}:{m}:{s}"
    instruction = instruction_text.get()
    alarms.append((set_alarm_timer, instruction))
    threading.Thread(target=alarm, args=(set_alarm_timer, instruction), daemon=True).start()

#5 - interface gráfica

"""
a seguir, será criado a janela do alarme, definindo:
1. a janela
2. titulo da janela
3. tamanho da janela e a sua posiçao inicial na tela
4. cor de fundo da janela
5. ícone da janela (opcional)
"""
clock = Tk()
clock.title("Alarm Clock")
clock.geometry("550x450+346+66")
clock.configure(bg="grey")
clock.iconbitmap(r"C:\Users\pedro\Desktop\pedro\programacao\python\projetos\alarm clock\clock.ico") # opcional

# 

row1 = Frame(clock, height=225, width=550)
row1.pack()

row2 = Frame(clock, height=225, width=550)
row2.pack()

# 
col1_row1 = Frame(row1, height=225, width=275, bg="grey")
col1_row1.pack(side=LEFT)

col2_row1 = Frame(row2, height=225, width=275, bg="red")
col2_row1.pack(side=LEFT)

col1_row2 = Frame(row1, height=225, width=275, bg="blue")
col1_row2.pack(side=LEFT)

col2_row2 = Frame(row2, height=225, width=275, bg="green")
col2_row2.pack(side=LEFT)

#

horizontal_line = Frame(height=3, bg="black")
horizontal_line.place(x=0, y=225, width=550)

#

vertical_line1 = Frame(width=3, bg="black")
vertical_line1.place(x=275, y=0, height=450)


""" a seguir, serão criados os rótulos (labels) que serão usados na interface gráfica, respectivamente:
1. a criação do alarme
2. a instrução de hora, minuto e segundo
3. o aviso do formato que deve ser usado
"""

setYourAlarm = Label(clock, text="Create an alarm", bg="black", fg="lightblue", font=("helvetica", 13, "bold"))
setYourAlarm.place(x=110, y=5)

main_clock = Label(clock, text="19:53:45", font=("helvetica", 25, "bold"), bg="black", fg="lightblue")
main_clock.place(x=110, y=35)

addTime = Label(clock, text="Hour   Minute   Second", bg="black", fg="white", font=60)
addTime.place(x=93.5, y=87)

time_format = Label(clock, text="Enter time in 24-hour format!", fg="red", bg="black", font="Arial")
time_format.place(x=73.5, y=390)

# variáveis que serão usadas para armazenar os valores de hora, minuto e segundo
hour = StringVar()
minute = StringVar()
second = StringVar()

# a seguir, serão criados os campos de entrada (Entry) para hora, minuto e segundo,
# onde o usuário poderá inserir os valores desejados
hourTime = Entry(clock, textvariable=hour, bg="pink", width=3, font = ("Arial", 15))
hourTime.place(x=93.5, y=117)

minuteTime = Entry(clock, textvariable=minute, bg="pink", width=3, font = ("Arial", 15))
minuteTime.place(x=150, y=117)

secondTime = Entry(clock, textvariable=second, bg="pink", width=3, font = ("Arial", 15))
secondTime.place(x=209, y=117)

# botão para criar o alarme, quando pressionado, ele chama a função actual_time que define o alarme
submit = Button(clock, text="Set Alarm", bg="black", fg="white", width=10, command=actual_time)
submit.place(x=135, y=190)

# criação da caixa de instrução, onde o usuário pode inserir o que deseja ser lembrado
instruction_text = StringVar(value="What should i remind you of?")
instruction_entry = Entry(clock, textvariable=instruction_text, fg="black", width=24, font=("Arial", 11))
instruction_entry.place(x=77, y=157)
instruction_entry.bind("<FocusIn>", clear_instruction)

# início do loop principal da interface gráfica
clock.mainloop()



"""
// criar mais "slots" de alarmes - feita uma lista de alarmes pra poder existir mais de 1 ( [] )
// resolver o problema com o vineboom.wav nao ter o path reconhecido - usar a biblioteca os para o arquivo ter acesso ao diretório do programa e poder usar os arquivos desse diretorio
//TODO: criar mais slots visualmente, e mais botoes pra setar os alarmes
//TODO: criar um botão para deletar o alarme
//TODO: replicar o nome de instruçao nesses slots
//TODO: criar um relogio/data principal na janela
//TODO: explicar a partir da linha #66
// descobrir como fazer pra janela nao ficar "nao respondendo" enquanto o tempo roda - tava rodando tudo em 1 thread só, agora ta multi
//TODO: melhorar a gui pra ser mais agradavel visualmente
// fazer o programa entender que se nenhum numero for colocado = 00 - .replace(" ", ""), explicaçao na linha 36-38
"""