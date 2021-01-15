#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 12:55:30 2019

# SETTINGS FROM DUNSMOOR (novelty-extinction)
# CS 6000-7000 (max 3 CS+/CS- in a row)
# ITI 9500-11500
# ACQ: 20/12 CS+ (12 shock) and 20 CS- (first 2 excluded and 3rd alwasy shock)
# shock 200ms
# EXT: 24 CS+ and 24 CS-
# Next day:
# REC: 12 CS+ and 13 CS-, first always CS- and second counterbalanced

@author: lindadevoogd
"""



import random as rnd
import sys
import os


#paths
mac=0
homepath="P:\Linda"
projectpath=os.path.join(homepath,'projects','FCWML_fMRI')

sys.path.append(os.path.join('C:\\','Users','linda','Google Drive','projects','_generalscripts'))
from stimfuncs import resrand, makeiti, savetxt                                #own function  

# STIMULUS SETTINGS
#------------------------------------------------------------------------------
n_csp=16 # per run
n_runs=2
n_trials = [[16,10],[10,10],[10,11]] #acq/ext, cs+/cs-
n_shocks = 6
maxrepetions = 3
dur_cs = [6000]    #jittered
dur_iti = [3000,7000]  #jittered
dur_nback = 15000

# Loop over subjects
c_subj = 1
studycode= "MRI_FCWML"

headers=['Phase', 'CBcode', 'CSPsnake', 'CS', 'CSdur', 'Shock', 'Condition', 'ITI']

for c_sex in ["f","m"]:
    for c_man in ["c","h"]:
        for c_face in [1,2]:
            for c_rec in ["pm","mp"]:
                for c_rep in range(4):
                    
                    # Counter balancing code
                    cb_code=c_sex+c_man+str(c_face)+c_rec
                    
                    #subj
                    if c_subj < 10:
                        subj_code = studycode + "00" + str(c_subj)
                    elif c_subj < 100:
                        subj_code = studycode + "0" + str(c_subj)
                        
                    # First position is the CS+ and second is the CS-
                    if c_face == 1:
                        cb_order=[1,2]
                    elif c_face == 2:
                        cb_order=[2,1]

                    # Loop over phases
                    for c_phase,n_phase in enumerate(["acquisition","extinction","recall"]):

                        #make list
                        if n_phase == "acquisition":
                            
                            for c_runs in range(n_runs):
                                
                                #which CS+s will be shocked OLD
                                #l_shock_pos = rnd.sample(range(3, int(n_csp/2)), int(n_shocks/2)-1)
                                #l_shock_pos = l_shock_pos + rnd.sample(range(int(n_csp/2), n_csp), int(n_shocks/2))
                                
                                #run1: first 2 trials always one CS+ and one cs- and 3 CS is always CS+ shock
                                if c_runs == 0:
                            
                                    #make list
                                    l_trials = [cb_order[0]] * (n_trials[c_phase][0]-2) + [cb_order[1]] * (n_trials[c_phase][1]-1)
                                
                                    #shuffle trial order 
                                    l_trials,ind=resrand(l_trials,maxrepetions)
                                    
                                    #restriction [first 2 discarded 3rd alwasy CS+ reinforced]
                                    l_trials = rnd.sample(range(1,3),2) + [cb_order[0]] + l_trials
                                    
                                    #create factor lists
                                    l_cs = ["CSP" if x==c_face else "CSM" for x in l_trials]
                                    
                                    #place shock in vectore
                                    l_csp=[i for i, j in enumerate(l_cs) if j == "CSP"]
                                    
                                    # shocks
                                    l_shock=[0] * len(l_cs)
                                    l_shock_pos = rnd.sample(range(3, n_csp), n_shocks-1)
                                    l_shock[2]=1
                                    
                                elif c_runs == 1:
                                    
                                    #make list
                                    l_trials = [cb_order[0]] * (n_trials[c_phase][0]) + [cb_order[1]] * (n_trials[c_phase][1])
                                
                                    #shuffle trial order 
                                    l_trials,ind=resrand(l_trials,maxrepetions)
                                    
                                    #create factor lists
                                    l_cs = ["CSP" if x==c_face else "CSM" for x in l_trials]
                                    
                                    #place shock in vectore
                                    l_csp=[i for i, j in enumerate(l_cs) if j == "CSP"]
                                    
                                    #shocks
                                    l_shock=[0] * len(l_cs)
                                    l_shock_pos = rnd.sample(range(1, n_csp), n_shocks)
                                                                
                                #add to vec
                                for i in l_shock_pos:
                                    l_shock[l_csp[i]]=1
    
                                #durations
                                l_dur_cs = dur_cs * len(l_trials)
                                l_dur_iti = makeiti(l_trials,dur_iti)  
                                
                                #add nback duur
                                l_dur_iti = [i + dur_nback for i in l_dur_iti]
                                
                                #combine
                                l_cb_code = [cb_code] * len(l_trials)
                                l_phase = ["acq"]  * len(l_trials)
                                l_man = ["fix"] * len(l_trials)
                                l_acq=[l_phase,l_cb_code,l_trials,l_cs,l_dur_cs,l_shock,l_man,l_dur_iti]
                                l_acq=list(map(list, zip(*l_acq))) #flip
                                
                                #save
                                l_acq.insert(0,headers)
                                savetxt(l_acq, "day1_run" + str(c_runs+1) + "_" + subj_code + ".txt")
                            
                        elif n_phase == "extinction":
                            
                            for c_runs in range(n_runs):
                                
                                #make list
                                l_trials = [cb_order[0]] * (n_trials[c_phase][0]-2) + [cb_order[1]] * (n_trials[c_phase][1]-1)
                            
                                #shuffle trial order 
                                l_trials,ind=resrand(l_trials,maxrepetions)
                                
                                #restriction [first 2 discarded 3rd alwasy CS+ reinforced]
                                l_trials = rnd.sample(range(1,3),2) + [cb_order[0]] + l_trials
                                
                                #create factor lists
                                l_cs = ["CSP" if x==c_face else "CSM" for x in l_trials]
                                
                                #make vectore with zeros
                                l_shock=[0] * len(l_cs)
                                
                                #durations
                                l_dur_cs = dur_cs * len(l_trials) 
                                l_dur_iti = makeiti(l_trials,dur_iti)
                                
                                #add nback duur
                                l_dur_iti = [i + dur_nback for i in l_dur_iti]
                                
                                #manipulation
                                if c_man == "c":
                                    l_man=["fix"] * len(l_trials)
                                elif c_man == "l":
                                    l_man = ["1back"] * len(l_trials)
                                elif c_man == "h":
                                    l_man = ["2back"] * len(l_trials)
                                    
    
                                #combine
                                l_cb_code = [cb_code] * len(l_trials)
                                l_phase = ["ext"]  * len(l_trials)
                                l_ext=[l_phase,l_cb_code,l_trials,l_cs,l_dur_cs,l_shock,l_man,l_dur_iti]
                                l_ext=list(map(list, zip(*l_ext))) #flip
                            
                                #save
                                l_ext.insert(0,headers)
                                savetxt(l_ext, "day1_run" + str(c_runs+3) + "_" + subj_code + ".txt")
                            
                            
                        elif n_phase == "recall":

                            for c_runs in range(n_runs):
                                
                                #make list
                                l_trials = [cb_order[0]] * (n_trials[c_phase][0]-1) + [cb_order[1]] * (n_trials[c_phase][1]-2)
                            
                                #shuffle trial order 
                                l_trials,ind=resrand(l_trials,maxrepetions)
                                
                                #first trial csm then 2 trials counterbalanced
                                if c_rec == "pm":
                                    if c_runs == 0:
                                        l_trials = [cb_order[1],cb_order[0],cb_order[1]] +l_trials
                                    elif c_runs == 1:
                                        l_trials = [cb_order[1],cb_order[1],cb_order[0]] +l_trials
                                elif c_rec == "mp":
                                    if c_runs == 0:
                                        l_trials = [cb_order[1],cb_order[1],cb_order[0]] +l_trials
                                    elif c_runs == 1:
                                        l_trials = [cb_order[1],cb_order[0],cb_order[1]] +l_trials
                                            
                                #create factor lists
                                l_cs = ["CSP" if x==c_face else "CSM" for x in l_trials]
    
                                #durations
                                l_dur_cs = dur_cs * len(l_trials)  
                                l_dur_iti = makeiti(l_trials,dur_iti)
                                
                                #add nback duur
                                l_dur_iti = [i + dur_nback for i in l_dur_iti]
                                
                                #combine
                                l_phase = ["rec"]  * len(l_trials)
                                l_cb_code = [cb_code] * len(l_trials)
                                l_shock=[0] * len(l_cs)
                                l_man = ["fix"] * len(l_trials)
                                l_rec=[l_phase,l_cb_code,l_trials,l_cs,l_dur_cs,l_shock,l_man,l_dur_iti]
                                l_rec=list(map(list, zip(*l_rec))) #flip
                                
                                #save
                                l_rec.insert(0,headers)
                                savetxt(l_rec, "day2_run" + str(c_runs+1) + "_" + subj_code + ".txt")
                            
                            c_subj+=1
