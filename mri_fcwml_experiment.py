# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 17:08:41 2018

# SETTINGS FROM DUNSMOOR (novelty-extinction) and DEVOOGD (emdr)
# CS = 6000 (max 3 CS+/CS- in a row)
# NBACK = 15000
# FIX = 3000-7000 (average 5000)
# ITI min/max = 18000-22000
#
# ACQ: run1=10/10/6  and run2=10/10/6 [CS-/CS+ur/CS+re]
# first 2 excluded and 3rd always a CS+ shock)
# shock 200ms
#
# EXT: run1=10/10 and run2=10/10 [CS+/CS-]

# ADAPTED FROM THE FCWML_behavior version:
- incorporated 1back/2back in 1 script
- triallist are read in better

@author: lindadevoogd
"""

# Import libraries
import expyriment
import os
import shutil
import sys
import glob

# SET BEFORE THE EXPERIMENT
#------------------------------------------------------------------------------
TESTING = 0 # 1 or 0

# Settings
WHICH_DAY = sys.argv[1] #first argument [example: novext_experiment.py day1 run1]
WHICH_RUN = sys.argv[2] #second argument [example: novext_experiment.py day1 run1]
REFRESH_RATE = 60  # In Hz
WINDOW_SIZE = 1280,1040
frame = 1000 / REFRESH_RATE


# MRI SETTINGS
#------------------------------------------------------------------------------
# Trigger is a USB connection and thus works the same as the keyboard [on number 5]
SCAN_TRIGGER_START = 6
SCAN_TRIGGER = expyriment.misc.constants.K_5
trigger = expyriment.io.Keyboard() 

# Keyboard
keys = expyriment.io.Keyboard() #buttonbox works same as a USB keyboard
keys.set_quit_key(expyriment.misc.constants.K_ESCAPE)#with esc you can quit
responsekey=[expyriment.misc.constants.K_1,
             expyriment.misc.constants.K_2,
             expyriment.misc.constants.K_3,
             expyriment.misc.constants.K_4,
             expyriment.misc.constants.K_6,
             expyriment.misc.constants.K_7,
             expyriment.misc.constants.K_8,
             expyriment.misc.constants.K_9] #1-4 and 6-9
experimenterkey=expyriment.misc.constants.K_g #so pp cannot accidently press space bar and continue

# TESTING
#------------------------------------------------------------------------------
# When testing
if TESTING == 1:
    #expyriment.control.set_develop_mode() #create small screen
    speedup = 100 # if set at 1 it is normal duration
    portconnected = 0 #no port connected
    eyelinkconnected=0
else:
    speedup = 1 #normal speed
    portconnected = 1 #port connected
    eyelinkconnected=1

# EYELINK CALIBRATION
#------------------------------------------------------------------------------
# Eyelink
if eyelinkconnected == 1:
    import pygaze
    import calibrate
    tracker = calibrate.cal()
    
# TASK SETTINGS
#------------------------------------------------------------------------------

# Create experimental task
task = expyriment.design.Experiment(name= "FCWML_fMRI",         #name of exp
        background_colour = (125,125,125))  #background color
expyriment.control.initialize(task)
task.add_data_variable_names(["Logevent","Onset","Key","RT"])


# START [so you can give exp input]
#------------------------------------------------------------------------------
# Start
if eyelinkconnected == 1:
    expyriment.control.start(skip_ready_screen=True,subject_id=int(calibrate.log_file))
else:
    expyriment.control.start(skip_ready_screen=True)

#subject codes 101,201,301 etc are run as 001 [according to the counterbalancing sheet]
if task.subject < 10:
    SUBJ_CODE = "MRI_FCWML00" + str(task.subject)
    edffilename=SUBJ_CODE
elif task.subject < 100:
    SUBJ_CODE = "MRI_FCWML0" + str(task.subject)
    edffilename=SUBJ_CODE
else:
    SUBJ_CODE = "MRI_FCWML0" + str(task.subject)[1:]
    edffilename="MRI_FCWML" + str(task.subject)


# PORT SETTINGS
#------------------------------------------------------------------------------
# Port setting [1=CS, 4=Shock, 8= Run]
if portconnected == 1:
    port = expyriment.io.ParallelPort(0xC020)
    port.send(0) # to make sure it is off!
port_biopack = 9 #code CS [1 + Run]
port_shock = [13,200] #code Shock [4 + CS + Run] and duration (although duration is set at the shock box)
port_run = 8
    


# STIMULUS SETTINGS
#------------------------------------------------------------------------------

# Get txt file [phase,code,face,cs,csdur,shock,man,iti]
triallistfile="triallist/" + WHICH_DAY + "_" + WHICH_RUN + "_" + SUBJ_CODE + ".txt"
with open(triallistfile) as f:
    for c,line in enumerate(f):        
        if c==0:            
            triallistnames=line.replace("'","").replace("[","").replace("]","").replace("\n","").split(', ')
            triallist = [ [] for val in range(len(triallistnames))]                  
        else:
            dat=line.replace("'","").replace("[","").replace("]","").replace("\n","").split(', ')
            for i,val in enumerate(dat):
                triallist[i].append(val)

#n-back
n_dig = 10
dur_dig = 1100
dur_digfix = 400
dur_fix = (dur_dig + dur_digfix) * n_dig
    
# DESIGN [experiment/task, blocks, trials, stimuli]
#------------------------------------------------------------------------------
# Create design (blocks and trials)
# Create stimuli (and put them into trials)
# Create input/output devices (like button boxes etc.)

# Loop over blocks [Acquisition and Extinction]

# One block so no loop
block = expyriment.design.Block("Block")

# Create Design, Loop over trials
for c_trials in range(len(triallist[0])):
    
    # Trial [define properties]
    trial =  expyriment.design.Trial()
    for c,name in enumerate(triallistnames):
        trial.set_factor(name,triallist[c][c_trials])   

    # Load CS pictures
    stim = expyriment.stimuli.Picture("stimuli/i_snake" + triallist[2][c_trials] + ".png")
    stim.preload()
    
    # Add stim to trial and trial to block
    trial.add_stimulus(stim)
    block.add_trial(trial)

# Add block to task
task.add_block(block)

# Create digit
stim_dig = []
n_seq = [1,2,3,4,5]
for c_dig in n_seq:
    dig = expyriment.stimuli.TextLine(text="{0}".format(c_dig),
                                      text_size=50,
                                      text_colour=[60,60,255])
    dig.preload()
    stim_dig.append(dig)
rnd=expyriment.design.randomize.rand_element

# Other stimuli
fixcross = expyriment.stimuli.FixCross(colour=(60,60,255))                      # default fixation cross
fixcross.preload()
blank = expyriment.stimuli.BlankScreen()                                        # blankscreen
blank.preload()

# Reinstatement
dur_reinstatement = 10000
black = expyriment.stimuli.BlankScreen(colour=(0,0,0))                         # blackscreen
black.preload()

# Function waits for a duration while logging key presses
def wait(dur):
    task.keyboard.clear()
    task.clock.reset_stopwatch()
    while task.clock.stopwatch_time < int(frame * int(round((dur) / frame, 5))) - 2:
        task.keyboard.check(keys=responsekey)
        task.keyboard.check(keys=SCAN_TRIGGER)
        
def waituntill(dur):
    task.keyboard.clear()
    while task.clock.time < int(frame * int(round((dur) / frame, 5))) - 2:
        task.keyboard.check(keys=responsekey)
        task.keyboard.check(keys=SCAN_TRIGGER)
        

# RUN
#------------------------------------------------------------------------------

# Check subject code
expyriment.stimuli.TextLine(text="You are running: " + str(task.subject) + " " + WHICH_DAY +
                            " " + WHICH_RUN, text_colour=[0,0,0]).present()

# Start after N scan triggers
current_trig=1
while current_trig is not SCAN_TRIGGER_START:
    trigger.wait(SCAN_TRIGGER)  # Initial scanner sync
    current_trig+=1

# Eyelink [start recording]
if eyelinkconnected == 1:
    tracker.start_recording()
    tracker.log('START_TIME')
if portconnected == 1:
    port.send(port_run)
wait(2000)
    
# Starttime
starttime=endtime=task.clock.time
task.data.add(["starttime",task.clock.time,"None","None"]) #LOG

# Reinstatement
if WHICH_DAY=='day2' and WHICH_RUN=='run2':
    
    for c_sh in [1,2,3]:
        
        # Trial end time
        endtime=endtime+dur_reinstatement

        # send code to biopack [open]
        if portconnected == 1:
            port.send(port_biopack)
        if eyelinkconnected == 1:
            tracker.log('REINSTATEMENT_START')
        
        # blank screen
        black.present()
        waituntill(endtime/speedup)    
        
        #send shock
        if portconnected == 1:
            port.send(port_shock[0]) #send shock
            task.data.add(["shock",task.clock.time,"None","None"]) #LOG 

    # send code to biopack [close]
    if portconnected == 1:
        port.send(port_run) # to make sure it is off (send 8 so run stays on)!
    if eyelinkconnected == 1:
        tracker.log("REINSTATEMENT_STOP")

    # fixation screen
    fixcross.present()
    endtime=endtime+dur_reinstatement
    wait(dur_reinstatement/speedup)
    
    
# Loop over trials/blocks
for trial in task.blocks[0].trials:
    
    # Trial end time
    endtime=endtime+int(trial.get_factor("CSdur"))+int(trial.get_factor("ITI"))
     
    # CS presentation
    #--------------------------------------------------------------------------
    trial.stimuli[0].present()
    task.clock.reset_stopwatch() # Reset stopwatch each trial
    task.data.add(["Pic_" + trial.get_factor("CSPsnake"),task.clock.time,"None","None"]) #LOG    
    
    # send code to biopack [open]
    if portconnected == 1:        
        port.send(port_biopack)
    if eyelinkconnected == 1:
            tracker.log("CS_ONSET")
    
    #shock trials vs no shock trials
    if trial.get_factor("Shock") == "1":  
        
        # CS presentation duration [minus shock duration]
        csdur=(int(trial.get_factor("CSdur"))-port_shock[1])/speedup
        while task.clock.stopwatch_time < int(frame * int(round((csdur) / frame, 5))) - 2:
            task.keyboard.check(keys=responsekey)
        
        #send shock
        if portconnected == 1:
            port.send(port_shock[0]) #send shock
            if eyelinkconnected == 1:
                tracker.log("SHOCK")
            task.data.add(["shock",task.clock.time,"None","None"]) #LOG                                               
            
        #wait remaining duration
        csdur=(int(trial.get_factor("CSdur")))/speedup
        while task.clock.stopwatch_time < int(frame * int(round((csdur) / frame, 5))) - 2:
            task.keyboard.check(keys=responsekey)
        
    else:
        
        # CS presentation duration
        csdur=(int(trial.get_factor("CSdur")))/speedup
        while task.clock.stopwatch_time < int(frame * int(round((csdur) / frame, 5))) - 2:
            task.keyboard.check(keys=responsekey)  
    
    # send code to biopack [close]
    if portconnected == 1:        
        port.send(port_run) # to make sure it is off (send 8 so run stays on)!
    if eyelinkconnected == 1:
        tracker.log("CS_OFFSET")


    # ITI presentation
    #--------------------------------------------------------------------------
    if trial.get_factor("Condition") == "fix":
        
        # present fixation
        fixcross.present()
        task.data.add(["fixonset",task.clock.time,"None","None"]) #LOG
        waituntill(endtime/speedup)
        
    elif trial.get_factor("Condition") == "1back":
        
        # prepare block
        one_back = 0    
        
        #loop over random digits
        for d in range(n_dig):
            
            # Prepare trial
            task.keyboard.clear()
            responses = []

            # Draw random digit [in ~25% the case it is a 1-back]
            if one_back == 0:
                p_dig=rnd(stim_dig)
                t_nback="digonset_"
            elif rnd([1,2,3,4]) == 1:
                p_dig=stim_dig[one_back-1]
                t_nback="oneback_"
            else:
                temp_stim_dig=stim_dig[:] #copy list not variable otherwise changes are applied to original variable
                temp_stim_dig.pop(one_back-1) #remove nback
                p_dig=rnd(temp_stim_dig)
                t_nback="digonset_"
            
            #update counters
            one_back=int(p_dig.text)
        
            #present and log
            p_dig.present() 
            dig_onset = task.clock.time
            task.data.add([t_nback+p_dig.text,dig_onset,"None","None","None","None"])
            
            # Reset stopwatch each trial
            task.clock.reset_stopwatch()
            
            # Wait and log responses        
            while task.clock.stopwatch_time < int(frame * int(round((dur_dig/speedup) / frame, 5))) - 2:
                key = task.keyboard.check(keys=responsekey)
                if key is not None:
                    responses.append((key, task.clock.stopwatch_time))
            
            # Present black screen
            blank.present() 
            dig_time = task.clock.time - dig_onset
            dig_fix_onset = task.clock.time
            
            # Wait and log responses        
            while task.clock.stopwatch_time < int(frame * int(round(((dur_dig+dur_digfix)/speedup) / frame, 5))) - 2:
                key = task.keyboard.check(keys=responsekey)
                if key is not None:
                    responses.append((key, task.clock.stopwatch_time))  
    
            # Log first response        
            try:
                keypressed, RT = responses[0]
            except:
                RT = keypressed = None
    
            dig_fix_time = task.clock.time - dig_fix_onset
            
            #collect data
            task.data.add(["response_"+p_dig.text,task.clock.time,keypressed,RT,dig_time,dig_fix_time]) #LOG
        
        
    elif trial.get_factor("Condition") == "2back":
        
        # prepare block
        two_back = 0
        one_back = 0    
        
        #loop over random digits
        for d in range(n_dig):
            
            # Prepare trial
            task.keyboard.clear()
            responses = []
            
            # Draw random digit [in ~25% the case it is a 2-back]
            if two_back == 0:
                p_dig=rnd(stim_dig)
                t_nback="digonset_"
            elif rnd([1,2,3,4]) == 1:
                p_dig=stim_dig[two_back-1]
                t_nback="twoback_"
            else:
                temp_stim_dig=stim_dig[:] #copy list not variable otherwise changes are applied to original variable
                temp_stim_dig.pop(two_back-1) #remove nback
                p_dig=rnd(temp_stim_dig)
                t_nback="digonset_"
            
            #update counters
            two_back=one_back
            one_back=int(p_dig.text)
        
            #present and log
            p_dig.present() 
            dig_onset = task.clock.time
            task.data.add([t_nback+p_dig.text,dig_onset,"None","None","None","None"])
            
            # Reset stopwatch each trial
            task.clock.reset_stopwatch()
            
            # Wait and log responses        
            while task.clock.stopwatch_time < int(frame * int(round((dur_dig/speedup) / frame, 5))) - 2:
                key = task.keyboard.check(keys=responsekey)
                if key is not None:
                    responses.append((key, task.clock.stopwatch_time))
            
            # Present black screen
            blank.present() 
            dig_time = task.clock.time - dig_onset
            dig_fix_onset = task.clock.time
            
            # Wait and log responses        
            while task.clock.stopwatch_time < int(frame * int(round(((dur_dig+dur_digfix)/speedup) / frame, 5))) - 2:
                key = task.keyboard.check(keys=responsekey)
                if key is not None:
                    responses.append((key, task.clock.stopwatch_time))  
    
            # Log first response        
            try:
                keypressed, RT = responses[0]
            except:
                RT = keypressed = None
    
            dig_fix_time = task.clock.time - dig_fix_onset
            
            #collect data
            task.data.add(["response_"+p_dig.text,task.clock.time,keypressed,RT,dig_time,dig_fix_time]) #LOG
            
        
        # Present fixation remaining time
        #--------------------------------------------------------------------------
        fixcross.present()
        task.data.add(["fixonset",task.clock.time,"None","None"]) #LOG
        waituntill(endtime/speedup)

# Let BOLD go down
fixcross.present()
task.clock.reset_stopwatch()    

# Eyelink [END RECORDING]
if portconnected == 1:
    port.send(0)
if eyelinkconnected == 1:
    tracker.log('end_time')
    tracker.stop_recording()
    tracker.close()

#wait remaining 10 sec
while task.clock.stopwatch_time < int(frame * int(round((10000) / frame, 5))) - 2:
    task.keyboard.check(keys=responsekey)
    
# End
task.data.add(["endtime",task.clock.time,"None","None"]) #LOG 
expyriment.control.end()
    
# MOVE DATA
#--------------------------------------------------------------------------
# make directory
data_dir = os.path.join(task.data.directory, edffilename, WHICH_DAY)
event_dir = os.path.join(task.events.directory, edffilename, WHICH_DAY)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
if not os.path.exists(event_dir):
    os.makedirs(event_dir)
    
# Move folders
os.rename(task.data.fullpath, os.path.join(data_dir, WHICH_RUN+"_"+task.data.filename))
os.rename(task.events.fullpath, os.path.join(event_dir, WHICH_RUN+"_"+task.events.filename))
if eyelinkconnected == 1:
    os.rename(calibrate.log_file + '.EDF', os.path.join(data_dir, edffilename + WHICH_DAY + WHICH_RUN + '.EDF'))
