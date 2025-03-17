"""
Script to execute the full runplan as defined in runplan.txt
"""
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from time import sleep

#from Capture import Initialize, get_bias, get_dark
from Capture import capture

def execute(cam, runfile="runplan.txt"):
    folder = f"data/{datetime.now():%Y%m%d}"
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(folder)

    plan = pd.read_csv(runfile)
    print(plan)

    status = None
    for i,el in enumerate(plan.itertuples()):#rows(named=True)):
        if el.status:
            continue
        else:
            print(el)
            print(datetime.now())
            if el.type == "bias":
                if status!="covered":
                    input("Bias Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
                
                cam.setTemp(el.temp)
                cam.setGain(el.gain)
                cam.bias()
                if np.abs(cam.getTemp - el.temp) > 0.1:
                    while np.abs(cam.getTemp - el.temp) > 0.1:
                        sleep(1)
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium
                                
                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            elif el.type == "dark":
                if status!="covered":
                    input("Dark Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
                cam.setTemp(el.temp)
                cam.setGain(el.gain)
                cam.setTint(el.exptime)
                if np.abs(cam.getTemp - el.temp) > 0.1:
                    while np.abs(cam.getTemp - el.temp) > 0.1:
                        sleep(1)
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium

                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            elif el.type == "flat":
                if status!=el.level:
                    input("Illuminate to level: ", el.level)
                    status = el.level
                cam.setTemp(el.temp)
                cam.setGain(el.gain)
                cam.setTint(el.exptime)
                if np.abs(cam.getTemp - el.temp) > 0.1:
                    while np.abs(cam.getTemp - el.temp) > 0.1:
                        sleep(1)
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium
                
                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            else:
                raise NotImplementedError("")
            plan.loc[i, 'status'] = True
            plan.to_csv("runplan.txt")
            print(el)
    return 1