import time
from tkinter.constants import BOTTOM, CENTER, LEFT, RIGHT, TOP, W
import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import time
import re

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
pomodoro_elapsed = 0
pomodorobreak_elapsed = 0
pomodoro_paused = False
pomodoro_startdt = None
pomodoro_enddt = None
pomodoro_state = 0
pomodoro_total = 0
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

# HH:MM:SS addition of hms
def hms_add(x,y):
    s = int(x[6:8]) + int(y[6:8])
    m = (int(x[3:5]) + int(y[3:5])) * 60
    h = (int(x[0:2]) + int(y[0:2])) * 3600
    return hms(s+m+h)

# Return productivity amount for the day
def day_productivity():
    logs = []
    y = 0
    current_time = "00:00:00"
    total_time = "00:00:00"
    pattern = r"([\d][\d]:[\d][\d]:[\d][\d])"
    current_dt = datetime.datetime.now().strftime("%B %d")
    with open("prod.data","r+") as f:
        x = f.readlines()
    for elt in x:
        if current_dt in elt:
            res = re.search(pattern, elt)
            total_time = hms_add(res[1], current_time)
            current_time = total_time
            y = y + 1
    return "Today, you had {} sessions, totaling to a productive time of {}!".format(y,total_time)

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
    global pomodoro_desc 
    global pomodoro_dur
    global pomodoro_break
    global pomodoro_elapsed
    global pomodorobreak_elapsed
    global pomodoro_paused
    global pomodoro_startdt
    global pomodoro_enddt
    global pomodoro_state
    global pomodoro_total
    if savevars == None: # For updates that don't have input elements
        pass
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
    elif savevars == "pomodoro":
        pomodoro_dur = 0
        pomodoro_elapsed = 0
        pomodoro_break = 0
        pomodorobreak_elapsed = 0
        pomodoroinput_desc.delete("1.0","end")
        pomodoroinput_dur.delete("1.0","end")
        pomodoroinput_break.delete("1.0","end")
        pomodorolobby_start['state']="normal"
        pomodorolobby_pause['state']="disabled"
        pomodorolobby_stop['state']="disabled"
    elif savevars == "pacedlobby":
        paced_startdt = get_datetime()
        paced_desc = pacedinput_desc.get(1.0, "end-1c").strip()
        if paced_desc == "":
            messagebox.showinfo("Info","Please enter your type of productivity.")
            pacedframe.tkraise()
            return
        pacedlobbyconsole_text['text'] = "Let's work at our own pace!\nActivity: "+paced_desc
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
    elif savevars == "pomodorolobby":
        pomodoro_total = 0
        pomodoro_startdt = get_datetime()
        pomodoro_desc = pomodoroinput_desc.get(1.0, "end-1c").strip()
        if pomodoro_desc == "":
            messagebox.showinfo("Info","Please enter your type of productivity.")
            pomodoroframe.tkraise()
            return
        try:
            pomodoro_break = int(pomodoroinput_break.get(1.0, "end-1c").strip())
            pomodoro_break = pomodoro_break * 60 #Convert from minutes to seconds
        except:
            messagebox.showinfo("Info","Please enter an integer for break time (in minutes).")
            pomodoroinput_break.delete("1.0", "end")
            pomodoroframe.tkraise()
            return
        try:
            pomodoro_dur = int(pomodoroinput_dur.get(1.0, "end-1c").strip())
            pomodoro_dur = pomodoro_dur * 60 #Convert from minutes to seconds
            pomodorolobby_timer['text']=hms(pomodoro_dur)
        except:
            messagebox.showinfo("Info","Please enter an integer for time (in minutes).")
            pomodoroinput_dur.delete("1.0", "end")
            pomodoroframe.tkraise()
            return
        pomodorolobbyconsole_text['text'] = "Let's work using the pomodoro technique!\nProductivity: "+hms(pomodoro_dur)+"|Break: "+hms(pomodoro_break)+"\nActivity: "+pomodoro_desc
    frame.tkraise() # Brings frame up
# pacedcounter - thread funct for timer
def pacedcounter(time_display):
    global paced_timer
    global pacedlobby_start
    global pacedlobby_pause
    global pacedlobby_stop
    while True:
        if paced_paused == True:
            pacedlobby_start['state'] = "normal"
            pacedlobby_pause['state'] = "disabled"
            pacedlobby_stop['state'] = "normal"
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
    pacedlobby_start['state']="disabled" 
    pacedlobby_pause['state']="disabled"
    pacedlobby_stop['state']="disabled" 

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

# counter for timed mode
def timedcounter(time_display):
    global timed_dur
    global timed_elapsed
    global mainframe
    global mainconsole_text
    global timedlobby_start
    global timedlobby_pause
    global timedlobby_stop
    while timed_dur != timed_elapsed:
        if timed_paused == True:
            timedlobby_start['state']="normal"
            timedlobby_pause['state']="disabled"
            timedlobby_stop['state']="normal"
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
    timedlobby_start['state']="disabled"
    timedlobby_pause['state']="disabled"
    timedlobby_stop['state']="disabled"

# timed_stop - ends current timed session
def timed_stop(frame, label):
    global timed_enddt
    global timed_elapsed
    global timed_desc
    global timed_paused
    timed_enddt = get_datetime()
    timed_paused = True
    data = '"{}","{}","Timed","{}","{}"\n'.format(timed_startdt,timed_enddt,hms(timed_elapsed),timed_desc)
    with open("prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(timed_elapsed)+ "!\nWould you like to start again?"

# counter for pomodoro mode
def pomodorocounter(time_display):
    global pomodoro_dur
    global pomodoro_break
    global pomodoro_state
    global pomodoro_elapsed
    global mainframe
    global mainconsole_text
    global pomodorobreak_elapsed
    global pomodoro_total
    global pomodorolobby_start
    global pomodorolobby_pause
    global pomodorolobby_stop
    if pomodoro_state == 0:
        while pomodoro_dur != pomodoro_elapsed:
            if pomodoro_paused == True:
                pomodorolobby_start['state']="normal"
                pomodorolobby_pause['state']="disabled"
                pomodorolobby_stop['state']="normal"
                return
            time.sleep(1)
            time_display['text'] = hms(pomodoro_dur-pomodoro_elapsed)
            pomodoro_elapsed += 1
            pomodoro_total += 1
        # Alert here
        pomodoro_state = 1
        pomodoro_elapsed = 0
        pomodorocounter(time_display)
    elif pomodoro_state == 1:
        while pomodoro_break != pomodorobreak_elapsed:
            if pomodoro_paused == True:
                pomodorolobby_start['state']="normal"
                pomodorolobby_pause['state']="disabled"
                pomodorolobby_stop['state']="normal"
                return
            time.sleep(1)
            time_display['text'] = hms(pomodoro_break-pomodorobreak_elapsed)
            pomodorobreak_elapsed += 1
        # Alert here
        pomodoro_state = 0
        pomodorobreak_elapsed = 0
        pomodorocounter(time_display)

# pomodoro_start - starts / resumes pomodorotime
def pomodoro_start(time_display):
    global pomodoro_dur
    global pomodorolobby_start
    global pomodorolobby_pause
    global pomodorolobby_stop
    global pomodoro_paused
    global pomodoro_break
    pomodorolobby_start['state']="disabled"
    pomodorolobby_pause['state']="normal"
    pomodorolobby_stop['state']="normal"
    pomodoro_paused = False
    threading.Thread(target=pomodorocounter, args=(time_display,), daemon=True).start()

# pomodoro_pause - for pausing pomodoro_timer
def pomodoro_pause():
    global pomodoro_paused
    global pomodorolobby_start
    global pomodorolobby_pause
    global pomodorolobby_stop
    pomodoro_paused = True
    pomodorolobby_start['state']="disabled"
    pomodorolobby_pause['state']="disabled"
    pomodorolobby_stop['state']="disabled"

# pomodoro_stop - ends current pomodoro session
def pomodoro_stop(frame, label):
    global pomodoro_enddt
    global pomodoro_elapsed
    global pomodoro_desc
    global pomodoro_paused
    global pomodoro_total
    pomodoro_enddt = get_datetime()
    pomodoro_paused = True
    data = '"{}","{}","Pomodoro","{}","{}"\n'.format(pomodoro_startdt,pomodoro_enddt,hms(pomodoro_total),pomodoro_desc)
    with open("prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(pomodoro_total)+ "!\nWould you like to start again?"

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
                        bg=bg, borderwidth=1, command=lambda:ssframe(pomodoroframe, "pomodoro"))
mainpomodoro_button.pack(pady=10)
counter_label = tk.Label(main_input, text=day_productivity(), font=bigfont, wraplength=300)
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
pomodoroinput_text1 = tk.Label(pomodoro_input, text="I will be doing this activity:", bg=bg, font=font)
pomodoroinput_text1.pack(pady=1)
pomodoroinput_desc = tk.Text(pomodoro_input, font=font, width=30, height=1)
pomodoroinput_desc.pack(pady=1)
pomodoroinput_text2 = tk.Label(pomodoro_input, text="for this amount of time: (in minutes)", bg=bg, font=font)
pomodoroinput_text2.pack(pady=1)
pomodoroinput_dur = tk.Text(pomodoro_input, font=font, width=3, height=1)
pomodoroinput_dur.pack(pady=1)
pomodoroinput_text3 = tk.Label(pomodoro_input, text="taking a break after for this amount of time: (in minutes)", bg=bg, font=font)
pomodoroinput_text3.pack(pady=1)
pomodoroinput_break = tk.Text(pomodoro_input, font=font, width=3, height=1)
pomodoroinput_break.pack(pady=1)
pomodoroinput_start = tk.Button(pomodoro_input, text="Start", font=font, bg=bg, borderwidth=1, command=lambda:ssframe(pomodorolobby,"pomodorolobby"))
pomodoroinput_start.pack(pady=2)
pomodoroinput_back = tk.Button(pomodoro_input, text="Back to Main", font=font, bg=bg, borderwidth=1, command=lambda:ssframe(mainframe, None))
pomodoroinput_back.pack(pady=2)

# -- Pomodorolobby -- #
pomodorolobby_console = tk.Frame(pomodorolobby, bg=fg)
pomodorolobby_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
pomodorolobby_input = tk.Frame(pomodorolobby, bg=bg)
pomodorolobby_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of pomodorolobby
pomodorolobbyconsole_text = tk.Label(pomodorolobby_console, text="Let's Work!", 
                        bg=fg, justify=CENTER, font=bigfont, wraplength=300)
pomodorolobbyconsole_text.pack(pady=5, anchor="n")
pomodorolobby_timer = tk.Label(pomodorolobby_input, text='00:00:00', font=timefont, justify=CENTER, bg=bg)
pomodorolobby_timer.pack(anchor="n")
pomodorolobby_start = tk.Button(pomodorolobby_input, text='Start Now', width=13, font=bigfont, state="normal", command=lambda:pomodoro_start(pomodorolobby_timer))
pomodorolobby_start.pack(side="left", padx=0.5)
pomodorolobby_pause = tk.Button(pomodorolobby_input, text='Pause', width=13, font=bigfont, state="disabled", command=lambda:pomodoro_pause())
pomodorolobby_pause.pack(side="left", padx=0.5)
pomodorolobby_stop = tk.Button(pomodorolobby_input, text='End Session', width=13, font=bigfont, state="disabled", command=lambda:pomodoro_stop(mainframe, mainconsole_text))
pomodorolobby_stop.pack(side="left", padx=0.5)

# Mainloop
root.resizable(0,0)
root.mainloop()