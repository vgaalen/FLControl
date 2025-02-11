"""
Script to execute the full runplan as defined in runplan.txt
"""
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from Capture import Initialize, get_bias, get_dark
from Shutdown import exit

folder = f"data/{datetime.now():%Y%m%d}"
Path(folder).mkdir(parents=True, exist_ok=True)
print(folder)

plan = pd.read_csv("runplan.txt")
print(plan)

context = Initialize()

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
            get_bias(context, folder+'/'+el.name+'.fits', el.num_frames, el.temp, el.gain)
        elif el.type == "dark":
            if status!="covered":
                input("Dark Frame: Place the cover on the camara and press Enter.")
                status = "covered"
            get_dark(context, folder+'/'+el.name+'.fits', el.num_frames, 1/el.exptime, el.temp, el.gain)
        else:
            raise NotImplementedError("")
        # TODO: Add support for illuminated frames
        # df=pd.concat([plan[0:i], 
        #               plan[i].with_columns(status=True),
        #               plan[i+1:]])
        plan.loc[i, 'status'] = True
        plan.to_csv("runplan.txt")
        print(el)

exit(context, message="Complete", error=False)