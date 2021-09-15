import time
from tkinter.constants import BOTTOM, CENTER, LEFT, RIGHT, TOP, W
import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import time
import re
from datetime import timedelta
from tkinter import ttk
from playsound import playsound
import os

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

# Sound setting up, tts
alldone_sound = "data/all_done.mp3" # https://freesound.org/people/javapimp/sounds/439094/
done_sound = "data/done.wav" # https://freesound.org/people/nckn/sounds/256113/
tada_sound = "data/tada.wav" # https://freesound.org/people/Reitanna/sounds/242671/
quack_sound = "data/quack.wav" # https://freesound.org/people/Reitanna/sounds/242664/
takeabreak_sound = "data/break_sound.mp3" # Made through gTTS
letscontinue_sound = "data/breakover_sound.mp3" # Made through gTTS

# Configuration of data file

if os.path.exists("data/prod.data") == False:
    f = open("data/prod.data","w+")
    f.close()
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

# daily stats
def statsdaily(label):
    global stats_text
    duration = []
    monthday = []
    ctr = 0
    label.delete(*label.get_children())
    with open("data/prod.data","r+") as f:
        x = f.readlines()
    day_now = datetime.datetime.now().strftime("%B %d")
    re_month = r"([\w ,:]+)\,"
    for line in x:
        newline = line[1:].replace("\n","")
        line_elts = newline[:-1].split('","')
        day = re.search(re_month, line_elts[0])
        if day[1] == day_now:
            label.insert('','end',text='1', values=(day[1],line_elts[2],line_elts[3],line_elts[4]))
            duration.append(line_elts[3])
            monthday.append(day[1])
            ctr += 1
    label.pack()
    z = "00:00:00"
    dur_list = []
    for y in duration:
        z = hms_add(z,y)
        dur_list.append((int(y[0:2])*3600) + (int(y[3:5])*60) + int(y[6:8]))
    z = (int(z[0:2])*3600) + (int(z[3:5])*60) + int(z[6:8])
    average = hms(int(z/ctr))
    max_val = hms(max(dur_list))
    min_val = hms(min(dur_list))
    stats_text['text'] = "Average session time is {}\nLongest session time is {}\nShortest session time is {}\nTotal daily productivity time is {}".format(average, max_val, min_val, hms(z))

# weekly stats
def statsweekly(label):
    global stats_text
    duration = []
    monthday = []
    ctr = 0
    label.delete(*label.get_children())
    with open("data/prod.data","r+") as f:
        x = f.readlines()
    day_now = datetime.datetime.now()
    week = []
    week.append(day_now.strftime("%B %d"))
    i = 1
    while i != 7:
        week_ago = (day_now - timedelta(days=i)).strftime("%B %d")
        week.append(week_ago)
        i += 1
    re_month = r"([\w ,:]+)\,"
    for current_day in week:
        for line in x:
            newline = line[1:].replace("\n","")
            line_elts = newline[:-1].split('","')
            day = re.search(re_month, line_elts[0])
            if day[1] == current_day:
                label.insert('','end',text='1', values=(day[1],line_elts[2],line_elts[3],line_elts[4]))
                duration.append(line_elts[3])
                monthday.append(day[1])
                ctr += 1
    label.pack()
    z = "00:00:00"
    dur_list = []
    for y in duration:
        z = hms_add(z,y)
        dur_list.append((int(y[0:2])*3600) + (int(y[3:5])*60) + int(y[6:8]))
    z = (int(z[0:2])*3600) + (int(z[3:5])*60) + int(z[6:8])
    average = hms(int(z/ctr))
    max_val = hms(max(dur_list))
    min_val = hms(min(dur_list))
    stats_text['text'] = "SESSION Ave-{}|Longest-{}|Shortest-{}".format(average, max_val, min_val)
    i = 0
    month_time = {}
    while i != len(dur_list):
        if monthday[i] in month_time.keys():
            month_time[monthday[i]] += dur_list[i]
        else:
            month_time[monthday[i]] = dur_list[i]
        i += 1
    total_dur = 0
    for dur in month_time.values():
        total_dur = total_dur + dur
    daily_ave = total_dur/len(month_time) # Concern - change len(month_time) to 7 to accomodate days of the week without productivites
    weekly_ave = total_dur/7
    max_key = max(month_time, key=month_time.get)
    min_key = min(month_time, key=month_time.get)
    stats_text['text'] = "Longest session is {}, Shortest session is {}\nLongest daily time is {} on {}\nShortest daily time is {} on {}\nProductive Average is {}, Weekly Average is {}\n Total productivity time is {}".format(max_val, min_val, hms(month_time[max_key]),max_key,hms(month_time[min_key]),min_key, hms(daily_ave),hms(weekly_ave),hms(total_dur))

# monthly stats
def statsmonthly(label):
    global stats_text
    duration = []
    monthday = []
    ctr = 0
    label.delete(*label.get_children())
    with open("data/prod.data","r+") as f:
        x = f.readlines()
    month = datetime.datetime.now().strftime("%B")
    re_month = r"([\w ,:]+)\,"
    for line in x:
        newline = line[1:].replace("\n","")
        line_elts = newline[:-1].split('","')
        day = re.search(re_month, line_elts[0])
        if month in day[1]:
            label.insert('','end',text='1', values=(day[1],line_elts[2],line_elts[3],line_elts[4]))
            duration.append(line_elts[3])
            monthday.append(day[1])
            ctr += 1
    label.pack()
    z = "00:00:00"
    dur_list = []
    for y in duration:
        z = hms_add(z,y)
        dur_list.append((int(y[0:2])*3600) + (int(y[3:5])*60) + int(y[6:8]))
    z = (int(z[0:2])*3600) + (int(z[3:5])*60) + int(z[6:8])
    average = hms(int(z/ctr))
    max_val = hms(max(dur_list))
    min_val = hms(min(dur_list))
    i = 0
    month_time = {}
    while i != len(dur_list):
        if monthday[i] in month_time.keys():
            month_time[monthday[i]] += dur_list[i]
        else:
            month_time[monthday[i]] = dur_list[i]
        i += 1
    total_dur = 0
    for dur in month_time.values():
        total_dur = total_dur + dur
    daily_ave = total_dur/len(month_time) # Concern - change len(month_time) to day of the month to accomodate days without productivites
    monthly_ave = total_dur/int(datetime.datetime.now().strftime("%d"))
    max_key = max(month_time, key=month_time.get)
    min_key = min(month_time, key=month_time.get)
    stats_text['text'] = "Longest session is {}, Shortest session is {}\nLongest daily time is {} on {}\nShortest daily time is {} on {}\nProductive Average is {}, Weekly Average is {}\n Total productivity time is {}".format(max_val, min_val, hms(month_time[max_key]),max_key,hms(month_time[min_key]),min_key, hms(daily_ave),hms(monthly_ave),hms(total_dur))

# Return productivity amount for the day
def day_productivity():
    logs = []
    y = 0
    current_time = "00:00:00"
    total_time = "00:00:00"
    pattern = r"([\d][\d]:[\d][\d]:[\d][\d])"
    current_dt = datetime.datetime.now().strftime("%B %d")
    with open("data/prod.data","r+") as f:
        x = f.readlines()
    for elt in x:
        if current_dt in elt:
            res = re.search(pattern, elt)
            total_time = hms_add(res[1], current_time)
            current_time = total_time
            y = y + 1
    return "Today, you had {} sessions, totaling to a productive time of {}!".format(y,total_time)

# configure data/prod.data to fit our needs
def data_configure():
    fixed_data = ""
    with open("data/prod.data","r+") as f:
        x = f.readlines()
    for line in x:
        newline = line[1:].replace("\n","")
        newline = newline[:-1]
        line_elts = newline.split('","')
        re_month = r"([\w ,:]+)\,"
        mo_start = re.search(re_month, line_elts[0])
        mo_end = re.search(re_month, line_elts[1])
        if mo_start[1] != mo_end[1]:
            # Discrepancy found
            day_start = int(mo_start[1][-2:])
            day_end = int(mo_end[1][-2:])
            if day_start+1 != day_end:
                print("Discrepancy is too big (more than 1 day). Requesting for manual change. See data/prod.data for more information.")
                print("Data: ",line)
                messagebox.showinfo("Error","Discrepancy on data/prod.data is too big (more than 1 day). Requesting for manual change. See data/prod.data for more information. Update aborted.")
                return
            print("Found a discrepancy on line: Different start and end dates",line)
            start_time = line_elts[0].strip(mo_start[1])
            start_time = start_time.replace(", ","")
            start_time = datetime.datetime.strptime(start_time, "%I:%M %p")
            start_time = start_time.strftime("%H:%M:%S")
            end_time = line_elts[1].strip(mo_end[1])
            end_time = end_time.replace(", ","")
            end_time = datetime.datetime.strptime(end_time, "%I:%M %p")
            end_time = end_time.strftime("%H:%M:%S")
            duration = line_elts[3]
            if int(hms_add(start_time,duration)[0:2]) >= 24:
                print("Splitting data entry into 2.")
                new_enddt = mo_start[1]+", 11:59 PM"
                dur1 = timedelta(hours=23, minutes=59) - timedelta(hours=int(start_time[0:2]),minutes=int(start_time[3:5]))
                dur2 = timedelta(hours=int(duration[0:2]),minutes=int(duration[3:5]),seconds=int(duration[6:8])) - dur1
                temp = str(dur1).split(":")
                dur1 = "{:02d}:{:02d}:{:02d}".format(int(temp[0]),int(temp[1]),int(temp[2]))
                temp = str(dur2).split(":")
                dur2 = "{:02d}:{:02d}:{:02d}".format(int(temp[0]),int(temp[1]),int(temp[2]))
                edit_entry1 = '"{}","{}","{}","{}","{}"\n'.format(line_elts[0],new_enddt,line_elts[2],dur1,line_elts[4])
                print(edit_entry1)
                edit_entry2 = '"{}","{}","{}","{}","{}"\n'.format(mo_end[1]+", 12:00 AM",line_elts[1],line_elts[2],dur2,line_elts[4])
                print(edit_entry2)
                fixed_data = fixed_data + edit_entry1 + "\n"+ edit_entry2
            else:
                print("Renaming data into 1 day.")
                new_enddt = mo_start[1]+", 11:59 PM"
                edit_entry1 = '"{}","{}","{}","{}","{}"\n'.format(line_elts[0],new_enddt,line_elts[2],line_elts[3],line_elts[4])
                fixed_data = fixed_data + edit_entry1
                print(edit_entry1)
        else:
            fixed_data = fixed_data + line
    with open("data/prod.data","w+") as f2:
        f2.write(fixed_data)

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
    elif savevars == "stats":
        stats_label.delete(*stats_label.get_children())
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
    data_configure()
    paced_enddt = get_datetime()    
    paced_paused = True
    # Add fnx here to add 2 diff data if it finished on different days
    if datetime.datetime.now().strftime("%B %d") not in paced_startdt:
        pass
    data = '"{}","{}","Paced","{}","{}"\n'.format(paced_startdt,paced_enddt,hms(paced_timer),paced_desc)
    print(data)
    with open("data/prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(paced_timer)+ "!\nWould you like to start again?"
    counter_label['text']=day_productivity()

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
    i = 0
    while i != 4:
        playsound(done_sound)
        i += 1
    playsound(alldone_sound)
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
    data_configure()
    timed_enddt = get_datetime()
    timed_paused = True
    data = '"{}","{}","Timed","{}","{}"\n'.format(timed_startdt,timed_enddt,hms(timed_elapsed),timed_desc)
    # Add fnx here to add 2 diff data if it finished on different days
    with open("data/prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(timed_elapsed)+ "!\nWould you like to start again?"
    counter_label['text']=day_productivity()
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
            time_display['text'] = "Time to work!\n"+str(hms(pomodoro_dur-pomodoro_elapsed))
            pomodoro_elapsed += 1
            pomodoro_total += 1
        i = 0
        playsound(tada_sound)
        playsound(takeabreak_sound)
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
            time_display['text'] = "Take a break!\n"+str(hms(pomodoro_break-pomodorobreak_elapsed))
            pomodorobreak_elapsed += 1
        playsound(quack_sound)
        playsound(letscontinue_sound)
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
    data_configure()
    pomodoro_enddt = get_datetime()
    pomodoro_paused = True
    data = '"{}","{}","Pomodoro","{}","{}"\n'.format(pomodoro_startdt,pomodoro_enddt,hms(pomodoro_total),pomodoro_desc)
    # Add fnx here to add 2 diff data if it finished on different days
    with open("data/prod.data","a+") as f:
        f.write(data)
    frame.tkraise()
    label['text'] = "You were productive for " + hms(pomodoro_total)+ "!\nWould you like to start again?"
    counter_label['text']=day_productivity()
# Calling instances of the frames
timedframe = tk.Frame(root, bg=bg, width=350, height=300)
pacedframe = tk.Frame(root, bg=bg, width=350, height=300)
pomodoroframe = tk.Frame(root, bg=bg, width=350, height=300)
timedlobby = tk.Frame(root, bg=bg, width=350, height=300)
pacedlobby = tk.Frame(root, bg=bg, width=350, height=300)
pomodorolobby = tk.Frame(root, bg=bg, width=350, height=300)
stats = tk.Frame(root, bg=bg, width=350, height=300)
mainframe = tk.Frame(root, bg=bg, width=350, height=300) # Must always be at the bottom so it shows up first!
for frame in (timedframe, pacedframe, pomodoroframe, timedlobby, pacedlobby, pomodorolobby, stats, mainframe):
  frame.grid(row=0,column=0,sticky='nsew') # Show frames

# -- Mainframe -- #
main_console = tk.Frame(mainframe, bg=fg)
main_console.place(relwidth=0.95, relheight=0.25, relx=0.025, rely=0.025)
main_input = tk.Frame(mainframe, bg=bg)
main_input.place(relwidth=0.95, relheight= 0.65, relx=0.025, rely=0.3)
# Elements of mainframe
mainconsole_text = tk.Label(main_console, text="Hello, welcome back! Let's get your day started. What productivity will we be doing today?", 
                            bg=fg, justify=LEFT, font=font, wraplength=300)
mainconsole_text.pack(pady=3, side=TOP, anchor="n")
mainpaced_button = tk.Button(main_input, text="Own Pace", font=bigfont, bg=bg, 
                        borderwidth=1, command=lambda:ssframe(pacedframe, "paced"))
mainpaced_button.pack(pady=3)
maintimed_button = tk.Button(main_input, text="Timed", font=bigfont, bg=bg, 
                        borderwidth=1, command=lambda:ssframe(timedframe, "timed"))
maintimed_button.pack(pady=3)
mainpomodoro_button = tk.Button(main_input, text="Pomodoro/Modified", font=bigfont, 
                        bg=bg, borderwidth=1, command=lambda:ssframe(pomodoroframe, "pomodoro"))
mainpomodoro_button.pack(pady=3)
counter_label = tk.Label(main_input, text=day_productivity(), font=bigfont, wraplength=300)
counter_label.pack()
mainstats_button = tk.Button(main_input, text="See your stats!", font=bigfont, 
                        bg=bg, borderwidth=1, command=lambda:ssframe(stats, None))
mainstats_button.pack(pady=7)

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

# -- stats -- #
stats_console = tk.Frame(stats, bg=fg)
stats_console.place(relwidth=0.95, relheight=0.3, relx=0.025, rely=0.025)
stats_text = tk.Label(stats_console, text="Here's the fruit of your productivity:", font=font, justify=CENTER, bg=fg)
stats_text.pack(anchor="n", pady=2)
stats_frame = tk.Frame(stats, bg=fg)
stats_frame.place(relwidth=0.95, relheight=0.63, relx=0.025, rely=0.35)
stats_label = ttk.Treeview(stats_frame, column=("Date", "Type", "Duration", "Description"), show='headings', height=6)
stats_label.column("# 1", anchor=CENTER, width=90)
stats_label.heading("# 1", text="Date")
stats_label.column("# 2", anchor=CENTER, width=70)
stats_label.heading("# 2", text="Type")
stats_label.column("# 3", anchor=CENTER, width=70)
stats_label.heading("# 3", text="Duration")
stats_label.column("# 4", anchor=CENTER, width=100)
stats_label.heading("# 4", text="Description")
stats_label.pack()
stats_daily = tk.Button(stats_frame, text='Daily', width=8, font=bigfont, bg=bg, command=lambda:statsdaily(stats_label))
stats_daily.pack(side="left", padx=2)
stats_weekly = tk.Button(stats_frame, text='Weekly', width=8, font=bigfont, bg=bg, command=lambda:statsweekly(stats_label))
stats_weekly.pack(side="left", padx=2)
stats_alltime = tk.Button(stats_frame, text='Month', width=8, font=bigfont, bg=bg, command=lambda:statsmonthly(stats_label))
stats_alltime.pack(side="left", padx=2)
stats_back = tk.Button(stats_frame, text="Back to Main", width=11, font=bigfont, bg=bg, command=lambda:ssframe(mainframe, "stats"))
stats_back.pack(side="left", padx=2)

# Mainloop
data_configure()
root.resizable(0,0)
root.mainloop()