import time
from tkinter.constants import CENTER, LEFT, TOP, W
import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import time

# Styling
bg = "#E7D2CC" 
fg = "#EEEDE7"
hlights = "#ECF87F"
graytext = "#808080"
font = ("Calibri",10)
bigfont = ("Calibri",12)
timefont = ("Calibri",20)
hfont = ("Calibri", 12, "bold")

# gvars - paced
paced_desc = None
paced_timer = 0
paced_paused = False
paced_startdt = None
paced_enddt = None
# gvars - timed
timed_desc = None
timed_dur = None
timed_elapsed = 0
timed_paused = False
timed_startdt = None
timed_enddt = None
# gvars - pomodoro
pomodoro_desc = None
pomodoro_dur = None
pomodoro_break = None
# gvars - all

# MAIN
root = tk.Tk() # Holds the whole GUI structure
root.title('Productivity App')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# converts seconds to HMS
def hms(duration):
    H = int(duration // 3600)
    M = int((duration % 3600) // 60)
    S = int(duration - H*3600 - M*60)
    return "{:02d}:{:02d}:{:02d}".format(H,M,S)

# Returns current date & time
def get_datetime():
    return datetime.datetime.now().strftime("%B %d, %I:%M %p")

# ssframe - shows and saves variables of inputs, if any
def ssframe(frame, savevars):
    global paced_desc
    global pacedinput_desc
    global pacedlobbyconsole_text
    global paced_startdt
    global pacedinput_desc
    global paced_timer
    global paced_paused
    global pacedlobby_timer
    global timed_desc
    global timed_dur
    global timed_paused
    global timed_startdt
    global timed_enddt
    global timed_elapsed
    global timedinput_desc
    if savevars == None: # For updates that don't have input elements
        pass
    elif savevars == "pacedlobby":
        paced_startdt = get_datetime()
        paced_desc = pacedinput_desc.get(1.0, "end-1c").strip()
        if paced_desc == "":
            messagebox.showinfo("Info","Please enter your type of productivity.")
            pacedframe.tkraise()
            return
        pacedlobbyconsole_text['text'] = "Let's work at our own pace!\nActivity: "+paced_desc
    elif savevars == "paced":
        paced_timer = 0
        paced_paused = False
        pacedinput_desc.delete("1.0","end")
        pacedlobby_start['state']="normal"
        pacedlobby_pause['state']="disabled"
        pacedlobby_stop['state']="disabled"
        pacedlobby_timer['text']="00:00:00"
    elif savevars == "timed":
        timed_dur = 0
        timed_elapsed = 0
        timed_paused = False
        timedinput_desc.delete("1.0","end")
        timedinput_dur.delete("1.0", "end")
        timedlobby_start['state']="normal"
        timedlobby_pause['state']="disabled"
        timedlobby_stop['state']="disabled"
    elif savevars == "timedlobby":
        timed_startdt = get_datetime()
        timed_desc = timedinput_desc.get(1.0, "end-1c").strip()
        if timed_desc == "":
            messagebox.showinfo("Info","Please enter your type of productivity.")
            timedframe.tkraise()
            return
        try:
            timed_dur = int(timedinput_dur.get(1.0, "end-1c").strip())
            timed_dur = timed_dur * 60 #Convert from minutes to seconds
            timedlobby_timer['text']=hms(timed_dur)
            timedlobbyconsole_text['text'] = "Let's work until our timer finishes!\nActivity: "+timed_desc
        except:
            messagebox.showinfo("Info","Please enter an integer for the time (in minutes).")
            timedinput_dur.delete("1.0", "end")
            timedframe.tkraise()
            return
    elif savevars == "pomodoro":
        pass
    frame.tkraise() # Brings frame up

# pacedcounter - thread funct for timer
def pacedcounter(time_display):
    global paced_timer
    while True:
        if paced_paused == True:
            return
        time.sleep(1)
        time_display['text'] = hms(paced_timer)
        paced_timer += 1

# paced_start - for resuming/starting paced timer
def paced_start(time_display):
    global paced_timer
    global pacedlobby_start
    global pacedlobby_pause
    global pacedlobby_stop
    global paced_paused
    pacedlobby_start['state']="disabled"
    pacedlobby_pause['state']="normal"
    pacedlobby_stop['state']="normal"
    paced_paused = False
    threading.Thread(target=pacedcounter, args=(time_display,), daemon=True).start()

# paced_pause - pausing timer
def paced_pause(): 
    global paced_paused
    global pacedlobby_start
    global pacedlobby_pause
    global pacedlobby_stop
    paced_paused = True
    pacedlobby_start['state']="normal"
    pacedlobby_pause['state']="disabled"
    pacedlobby_stop['state']="normal"

# paced_stop - ends session
def paced_stop(frame,label):
    global paced_enddt
    global paced_timer
    global paced_desc
    global paced_paused
    paced_enddt = get_datetime()
    paced_paused = True
    data = '"{}","{}","Paced","{}","{}"\n'.format(paced_startdt,paced_enddt,hms(paced_timer),paced_desc)
    with open("prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(paced_timer)+ "!\nWould you like to start again?"

def timedcounter(time_display):
    global timed_dur
    global timed_elapsed
    global mainframe
    global mainconsole_text
    while timed_dur != timed_elapsed:
        if timed_paused == True:
            return
        time.sleep(1)
        time_display['text'] = hms(timed_dur-timed_elapsed)
        timed_elapsed += 1
    # ALERT HERE
    timed_stop(mainframe,mainconsole_text)

# timed_start - for resuming/starting timed_timer
def timed_start(time_display):
    global timed_dur
    global timedlobby_start
    global timedlobby_pause
    global timedlobby_stop
    global timed_paused
    timedlobby_start['state']="disabled"
    timedlobby_pause['state']="normal"
    timedlobby_stop['state']="normal"
    timed_paused = False
    threading.Thread(target=timedcounter, args=(time_display,), daemon=True).start()

# timed_pause - for pausing timed_timer
def timed_pause():
    global timed_paused
    global timedlobby_start
    global timedlobby_pause
    global timedlobby_stop
    timed_paused = True
    timedlobby_start['state']="normal"
    timedlobby_pause['state']="disabled"
    timedlobby_stop['state']="normal"

# timed_stop - ends current timed session
def timed_stop(frame, label):
    global timed_enddt
    global timed_elapsed
    global timed_desc
    global timed_paused
    timed_enddt = get_datetime()
    timed_paused = True
    data = '"{}","{}","timed","{}","{}"\n'.format(timed_startdt,timed_enddt,hms(timed_elapsed),timed_desc)
    with open("prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(timed_elapsed)+ "!\nWould you like to start again?"

# Calling instances of the frames
timedframe = tk.Frame(root, bg=bg, width=350, height=300)
pacedframe = tk.Frame(root, bg=bg, width=350, height=300)
pomodoroframe = tk.Frame(root, bg=bg, width=350, height=300)
timedlobby = tk.Frame(root, bg=bg, width=350, height=300)
pacedlobby = tk.Frame(root, bg=bg, width=350, height=300)
pomodorolobby = tk.Frame(root, bg=bg, width=350, height=300)
mainframe = tk.Frame(root, bg=bg, width=350, height=300) # Must always be at the bottom so it shows up first!
for frame in (timedframe, pacedframe, pomodoroframe, timedlobby, pacedlobby, pomodorolobby, mainframe):
  frame.grid(row=0,column=0,sticky='nsew') # Show frames

# -- Mainframe -- #
main_console = tk.Frame(mainframe, bg=fg)
main_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
main_input = tk.Frame(mainframe, bg=bg)
main_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of mainframe
mainconsole_text = tk.Label(main_console, text="Hello, welcome back! Let's get your day started. What productivity will we be doing today?", 
                            bg=fg, justify=LEFT, font=font, wraplength=300)
mainconsole_text.pack(pady=5, side=TOP, anchor="n")
mainpaced_button = tk.Button(main_input, text="Own Pace", font=bigfont, bg=bg, 
                        borderwidth=1, command=lambda:ssframe(pacedframe, "paced"))
mainpaced_button.pack(pady=10)
maintimed_button = tk.Button(main_input, text="Timed", font=bigfont, bg=bg, 
                        borderwidth=1, command=lambda:ssframe(timedframe, "timed"))
maintimed_button.pack(pady=10)
mainpomodoro_button = tk.Button(main_input, text="Pomodoro/Modified", font=bigfont, 
                        bg=bg, borderwidth=1, command=lambda:ssframe(pomodoroframe, None))
mainpomodoro_button.pack(pady=10)
counter_label = tk.Label(main_input, text="You've been productive for X minutes \n| hours today!", font=hfont, wraplength=300)
counter_label.pack()

# -- Pacedframe -- #
paced_console = tk.Frame(pacedframe, bg=fg)
paced_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
paced_input = tk.Frame(pacedframe, bg=bg)
paced_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of pacedframe
pacedconsole_text = tk.Label(paced_console, text="Let's do productivity at our own pace. What will we be doing?", 
                            bg=fg, justify=LEFT, font=font, wraplength=300)
pacedconsole_text.pack(pady=5, side=TOP, anchor="n")
pacedinput_text = tk.Label(paced_input, text="I will be doing this activity until I can:", bg=bg, font=bigfont)
pacedinput_text.pack(pady=2)
pacedinput_desc = tk.Text(paced_input, font=font, width=30, height=2)
pacedinput_desc.pack(pady=2)
pacedinput_start = tk.Button(paced_input, text="Start", font=bigfont, bg=bg, borderwidth=1, command=lambda:ssframe(pacedlobby, "pacedlobby"))
pacedinput_start.pack(pady=10)
pacedinput_back = tk.Button(paced_input, text="Back to Main", font=bigfont, bg=bg, borderwidth=1, command=lambda:ssframe(mainframe, None))
pacedinput_back.pack(pady=10)

# -- Pacedlobby -- #
pacedlobby_console = tk.Frame(pacedlobby, bg=fg)
pacedlobby_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
pacedlobby_input = tk.Frame(pacedlobby, bg=bg)
pacedlobby_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of pacedlobby
pacedlobbyconsole_text = tk.Label(pacedlobby_console, text="Let's Work!", 
                        bg=fg, justify=CENTER, font=bigfont, wraplength=300)
pacedlobbyconsole_text.pack(pady=5, anchor="n")
pacedlobby_timer = tk.Label(pacedlobby_input, text='00:00:00', font=timefont, justify=CENTER, bg=bg)
pacedlobby_timer.pack(anchor="n")
pacedlobby_start = tk.Button(pacedlobby_input, text='Start Now', width=13, font=bigfont, state="normal", command=lambda:paced_start(pacedlobby_timer))
pacedlobby_start.pack(side="left", padx=0.5)
pacedlobby_pause = tk.Button(pacedlobby_input, text='Pause', width=13, font=bigfont, state="disabled", command=lambda:paced_pause())
pacedlobby_pause.pack(side="left", padx=0.5)
pacedlobby_stop = tk.Button(pacedlobby_input, text='End Session', width=13, font=bigfont, state="disabled", command=lambda:paced_stop(mainframe, mainconsole_text))
pacedlobby_stop.pack(side="left", padx=0.5)


# -- Timedframe -- #
timed_console = tk.Frame(timedframe, bg=fg)
timed_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
timed_input = tk.Frame(timedframe, bg=bg)
timed_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of timedframe
timedconsole_text = tk.Label(timed_console, text="Let's do productivity for a set amount of time. What will we be doing?", 
                            bg=fg, justify=LEFT, font=font, wraplength=300)
timedconsole_text.pack(pady=5, side=TOP, anchor="n")
timedinput_text1 = tk.Label(timed_input, text="I will be doing this activity:", bg=bg, font=font)
timedinput_text1.pack(pady=2)
timedinput_desc = tk.Text(timed_input, font=font, width=30, height=2)
timedinput_desc.pack(pady=2)
timedinput_text2 = tk.Label(timed_input, text="for this amount of time: (in minutes)", bg=bg, font=font)
timedinput_text2.pack(pady=2)
timedinput_dur = tk.Text(timed_input, font=timefont, width=3, height=1)
timedinput_dur.pack(pady=2)
timedinput_start = tk.Button(timed_input, text="Start", font=font, bg=bg, borderwidth=1, command=lambda:ssframe(timedlobby,"timedlobby"))
timedinput_start.pack(pady=2)
timedinput_back = tk.Button(timed_input, text="Back to Main", font=font, bg=bg, borderwidth=1, command=lambda:ssframe(mainframe, None))
timedinput_back.pack(pady=2)

# -- Timedlobby -- #
timedlobby_console = tk.Frame(timedlobby, bg=fg)
timedlobby_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
timedlobby_input = tk.Frame(timedlobby, bg=bg)
timedlobby_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of timedlobby
timedlobbyconsole_text = tk.Label(timedlobby_console, text="Let's Work!", 
                        bg=fg, justify=CENTER, font=bigfont, wraplength=300)
timedlobbyconsole_text.pack(pady=5, anchor="n")
timedlobby_timer = tk.Label(timedlobby_input, text='00:00:00', font=timefont, justify=CENTER, bg=bg)
timedlobby_timer.pack(anchor="n")
timedlobby_start = tk.Button(timedlobby_input, text='Start Now', width=13, font=bigfont, state="normal", command=lambda:timed_start(timedlobby_timer))
timedlobby_start.pack(side="left", padx=0.5)
timedlobby_pause = tk.Button(timedlobby_input, text='Pause', width=13, font=bigfont, state="disabled", command=lambda:timed_pause())
timedlobby_pause.pack(side="left", padx=0.5)
timedlobby_stop = tk.Button(timedlobby_input, text='End Session', width=13, font=bigfont, state="disabled", command=lambda:timed_stop(mainframe, mainconsole_text))
timedlobby_stop.pack(side="left", padx=0.5)


# -- Pomodoroframe -- #
pomodoro_console = tk.Frame(pomodoroframe, bg=fg)
pomodoro_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
pomodoro_input = tk.Frame(pomodoroframe, bg=bg)
pomodoro_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of pomodoroframe
pomodoroconsole_text = tk.Label(pomodoro_console, text="Let's do productivity using the pomodoro technique. What will we be doing?", 
                            bg=fg, justify=LEFT, font=font, wraplength=300)
pomodoroconsole_text.pack(pady=5, side=TOP, anchor="n")

# Mainloop
root.resizable(0,0)
root.mainloop()