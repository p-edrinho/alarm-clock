#1 - importar as bibliotecas necessárias
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import datetime
import time
import threading
import os
import sys

#2 - definir a classe principal e seus metodos
class AlarmClock:
    def __init__(self):
        # Set working directory to script location
        if getattr(sys, 'frozen', False):
            # If running as executable
            os.chdir(os.path.dirname(sys.executable))
        else:
            # If running as script
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize alarm list
        self.all_alarms = []
        self.alarm_threads = []
        
        # Create main window
        self.setup_window()
        
        # Create GUI elements
        self.setup_gui()
        
        # Start the main clock
        self.update_main_clock()
    
    def setup_window(self):
        """Initialize the main window with proper settings"""
        self.clock = tk.Tk()
        self.clock.title("Alarm Clock")
        self.clock.geometry("300x300+346+66")
        self.clock.configure(bg="grey")
        self.clock.resizable(False, False)
        
        # Try to set icon, fail gracefully if not found
        try:
            self.clock.iconbitmap("clock.ico")
        except tk.TclError:
            print("Warning: clock.ico not found, using default icon")
        
        # Handle window closing
        self.clock.protocol("WM_DELETE_WINDOW", self.on_closing) # method to handle what should happen when the window is tried to be closed
    
    def setup_gui(self):
        """Create all GUI elements"""
        # Title label
        title_label = tk.Label(
            self.clock, 
            text="Create an alarm", 
            bg="black", 
            fg="lightblue", 
            font=("helvetica", 13, "bold")
        )
        title_label.place(x=85, y=5)
        
        # Main clock display
        self.time_now = tk.Label(
            self.clock, 
            text="", 
            font=("helvetica", 25, "bold"), 
            bg="black", 
            fg="lightblue"
        )
        self.time_now.place(x=82, y=35)
        
        # Time input labels
        tk.Label(self.clock, text="Hour", bg="black", fg="white", font=("Arial", 10)).place(x=70.5, y=87)
        tk.Label(self.clock, text="Minute", bg="black", fg="white", font=("Arial", 10)).place(x=120.5, y=87)
        tk.Label(self.clock, text="Second", bg="black", fg="white", font=("Arial", 10)).place(x=180.5, y=87)
        
        # Time input variables
        self.hour = tk.StringVar()
        self.minute = tk.StringVar()
        self.second = tk.StringVar()
        
        # Time input fields with validation
        self.hour_entry = tk.Entry(
            self.clock, 
            textvariable=self.hour, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.hour_entry.place(x=70.5, y=117)
        self.hour_entry.bind('<KeyRelease>', self.validate_hour)
        
        self.minute_entry = tk.Entry(
            self.clock, 
            textvariable=self.minute, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.minute_entry.place(x=127.5, y=117)
        self.minute_entry.bind('<KeyRelease>', self.validate_minute_second)
        
        self.second_entry = tk.Entry(
            self.clock, 
            textvariable=self.second, 
            bg="pink", 
            width=3, 
            font=("Arial", 15),
            justify='center'
        )
        self.second_entry.place(x=190.5, y=117)
        self.second_entry.bind('<KeyRelease>', self.validate_minute_second)
        
        # Instruction entry
        self.instruction_text = tk.StringVar(value="Reminder:")
        self.instruction_entry = tk.Entry(
            self.clock, 
            textvariable=self.instruction_text, 
            fg="black", 
            width=18, 
            font=("Arial", 11)
        )
        self.instruction_entry.place(x=76, y=157)
        self.instruction_entry.bind("<FocusIn>", self.clear_instruction)
        
        # Set alarm button
        submit_btn = tk.Button(
            self.clock, 
            text="Set Alarm", 
            bg="black", 
            fg="white", 
            width=10, 
            command=self.set_alarm,
            font=("Arial", 10)
        )
        submit_btn.place(x=110, y=190)
        
        # Add/Remove buttons with images or text fallback
        self.create_control_buttons()
        
        # Format instruction
        format_label = tk.Label(
            self.clock, 
            text="Enter time in 24-hour format!", 
            fg="red", 
            bg="black", 
            font=("Arial", 8)
        )
        format_label.place(x=79.5, y=275)
    
    def create_control_buttons(self):
        """Create add/remove buttons with image fallback"""
        # Try to load images
        plus_img = self.load_resized_image_with_circular_shadow("plus.png", 45, 45)
        minus_img = self.load_resized_image_with_circular_shadow("minus.png", 35, 35)
        
        # Add button 
        if plus_img:
            add_btn = tk.Button(
                self.clock, 
                image=plus_img, 
                bg="grey", 
                borderwidth=0, 
                highlightthickness=0, 
                relief="flat", 
                activebackground="grey"
            )
            add_btn.image = plus_img  # Keep a reference
        else:
            add_btn = tk.Button(
                self.clock, 
                text="+", 
                bg="white", 
                fg="black", 
                width=3, 
                height=1, 
                font=("Arial", 15)
            )
        add_btn.place(x=201, y=220)
        
        # Remove button 
        if minus_img:
            remove_btn = tk.Button(
                self.clock, 
                image=minus_img, 
                bg="grey", 
                borderwidth=0, 
                highlightthickness=0, 
                relief="flat", 
                activebackground="grey"
            )
            remove_btn.image = minus_img  # Keep a reference
        else:
            remove_btn = tk.Button(
                self.clock, 
                text="-", 
                bg="white", 
                fg="black", 
                width=3, 
                height=1, 
                font=("Arial", 15)
            )
        remove_btn.place(x=68, y=220)
        
        # Store button references for later use
        self.add_btn = add_btn
        self.remove_btn = remove_btn
    
    def validate_hour(self, event=None):
        """Validate hour input (0-23)"""
        value = self.hour.get()
        if value and not value.isdigit():
            self.hour.set(''.join(c for c in value if c.isdigit()))
        elif value and int(value) > 23:
            self.hour.set('23')
    
    def validate_minute_second(self, event=None):
        """Validate minute/second input (0-59)"""
        widget = event.widget if event else None
        if widget == self.minute_entry:
            var = self.minute
        else:
            var = self.second
        
        value = var.get()
        if value and not value.isdigit():
            var.set(''.join(c for c in value if c.isdigit()))
        elif value and int(value) > 59:
            var.set('59')
    
    def load_resized_image_with_circular_shadow(self, image_path, max_width, max_height):
        """Load and resize image with circular shadow effect"""
        try:
            # Load and resize the original image
            image = Image.open(image_path).convert("RGBA")
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Create a larger canvas for shadow
            shadow_offset = 3
            canvas_size = (max_width + shadow_offset * 2, max_height + shadow_offset * 2)
            canvas = Image.new('RGBA', canvas_size, (128, 128, 128, 0))
            
            # Create circular shadow
            shadow_size = min(image.size)
            shadow_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            
            # Draw circular shadow
            shadow_pos = (shadow_offset + 2, shadow_offset + 2)
            shadow_end = (shadow_pos[0] + shadow_size, shadow_pos[1] + shadow_size)
            shadow_draw.ellipse([shadow_pos, shadow_end], fill=(0, 0, 0, 60))
            
            # Blur the shadow
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(2))
            
            # Composite shadow and image
            canvas = Image.alpha_composite(canvas.convert('RGBA'), shadow_img)
            image_pos = (shadow_offset, shadow_offset)
            canvas.paste(image, image_pos, image)
            
            return ImageTk.PhotoImage(canvas)
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None
    
    def clear_instruction(self, event):
        """Clear instruction text when focused"""
        if self.instruction_text.get() == "Reminder:":
            self.instruction_text.set("")
    
    def update_main_clock(self):
        """Update the main clock display every second"""
        current_time = datetime.datetime.now()
        now = current_time.strftime("%H:%M:%S")
        self.time_now.config(text=now)
        self.clock.after(1000, self.update_main_clock)
    
    def set_alarm(self):
        """Set a new alarm"""
        try:
            # Get time values with defaults
            h = self.hour.get().strip() if self.hour.get().strip() else "00"
            m = self.minute.get().strip() if self.minute.get().strip() else "00"
            s = self.second.get().strip() if self.second.get().strip() else "00"
            
            # Validate and format time
            h = f"{int(h):02d}" if h.isdigit() and 0 <= int(h) <= 23 else "00"
            m = f"{int(m):02d}" if m.isdigit() and 0 <= int(m) <= 59 else "00"
            s = f"{int(s):02d}" if s.isdigit() and 0 <= int(s) <= 59 else "00"
            
            set_alarm_timer = f"{h}:{m}:{s}"
            instruction = self.instruction_text.get() if self.instruction_text.get() != "Reminder:" else "Time's up!"
            
            # Check if alarm time is in the future
            current_time = datetime.datetime.now()
            alarm_time = datetime.datetime.strptime(set_alarm_timer, "%H:%M:%S")
            alarm_datetime = current_time.replace(
                hour=alarm_time.hour,
                minute=alarm_time.minute,
                second=alarm_time.second,
                microsecond=0
            )
            
            # If alarm time is for tomorrow
            if alarm_datetime <= current_time:
                alarm_datetime += datetime.timedelta(days=1)
            
            # Add alarm to list
            alarm_info = {
                'time': set_alarm_timer,
                'instruction': instruction,
                'datetime': alarm_datetime,
                'active': True
            }
            self.all_alarms.append(alarm_info)
            
            # Start alarm thread
            alarm_thread = threading.Thread(
                target=self.alarm_worker, 
                args=(set_alarm_timer, instruction), 
                daemon=True
            )
            alarm_thread.start()
            self.alarm_threads.append(alarm_thread)
            
            messagebox.showinfo("Alarm Set", f"Alarm set for {set_alarm_timer}\nReminder: {instruction}")
            
            # Clear inputs
            self.hour.set("")
            self.minute.set("")
            self.second.set("")
            self.instruction_text.set("Reminder:")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set alarm: {str(e)}")
    
    def alarm_worker(self, set_alarm_timer, instruction):
        """Worker thread for alarm monitoring"""
        try:
            while True:
                time.sleep(1)
                current_time = datetime.datetime.now()
                now = current_time.strftime("%H:%M:%S")
                
                if now == set_alarm_timer:
                    print(f"Time's up! Reminder: {instruction}")
                    self.play_alarm_sound()
                    
                    # Show alarm notification
                    self.clock.after(0, lambda: messagebox.showinfo("Alarm!", f"Time's up!\nReminder: {instruction}"))
                    break
        except Exception as e:
            print(f"Alarm error: {e}")
    
    def play_alarm_sound(self):
        """Play alarm sound with fallback"""
        try:
            import winsound
            # Try to play custom sound
            if os.path.exists("vineboom.wav"):
                winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | winsound.SND_NOWAIT)
                time.sleep(0.5)
                winsound.PlaySound("vineboom.wav", winsound.SND_FILENAME | winsound.SND_NOWAIT)
            else:
                # Fallback to system beep
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except ImportError:
            # For non-Windows systems, just print
            print("\a")  # System bell
    

    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.clock.destroy()
    
    def run(self):
        """Start the application"""
        self.clock.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = AlarmClock()
    app.run()

# TODO: adicionar uma forma de escolher seu proprio som pro alarme?
# TODO: melhorar a gui pra ser mais agradavel visualmente
# TODO: feito os botoes de adicionar/remover mais alarmes, fazer com que cada botão de remover, remova seu proprio alarme e depois fazer um botao universal de adicionar
# TODO: criar mais slots visualmente, e mais botoes pra setar os alarmes
# TODO: criar um botão para deletar o alarme
