"""
Script to execute the full runplan as defined in runplan.txt
"""
import numpy as np
# try:
#     import polars as pd
# except:
import pandas as pd
from datetime import datetime
from pathlib import Path
from time import sleep
import threading

from Capture import capture


class ContinuousCapture:
    def __init__(self, capture_function, function_arguments):
        self.capture = capture_function
        self.running = False
        self.loop = None
        self.fun_args = function_arguments
        print("ContinuousCapture Initialized")

    def start_thread(self):
        print("Starting the Thread")
        self.running = True
        #self.capture(*self.fun_args)
        self.thread = threading.Thread(target=self.loop)#, args=(self.fun_args))  # , args = (interval))
        self.thread.start()
        print("Thread Running", self.running)
        # ToDo fix the loop

    def stop_thread(self):
        self.running = False

    def loop(self):
        print("Loop Started")
        while self.running:
            self.capture(*self.fun_args)
            sleep(60*10)
        print("Loop Stopped")


class ProgrammedCapture:
    def __init__(self, cam, file="runplan.csv", progress_func=None, exit_status_func=None):
        self.cam = cam
        self.file
        self.progress_func = progress_func
        self.exit_status_func = exit_status_func
        self.itt = 0
        self.status = None
        self.running = False
        self.loop = None

        self.out_dir = f"data/{datetime.now():%Y%m%d}"
        Path(self.out_dir).mkdir(parents=True, exist_ok=True)

        self.program = pd.read_csv(file)
        print(self.program)
        self.n = len(self.program)

    def start_thread(self):
        self.running = True
        self.loop = threading.Thread(target=self.loop)  # , args = (interval))
        self.loop.start()

    def stop_thread(self):
        self.running = False

    def loop(self):
        while self.running:
            self._next_line()

    def _next_line(self):
        if self.itt >= self.n:
            self.exit_status_func("Complete")
            self.running = False
            return True

        self.progress_func(itt=self.itt, range=self.n)
        entry = self.program.loc[self.itt]
        if entry.status:
            return True
        else:
            print(entry)
            print(datetime.now())
            self.cam.setTemp(entry.temp)
            self.cam.setGain(entry.gain)
            self.cam.setFps(entry.fps)
            self.cam.setExptime(entry.exptime)
            if np.abs(self.cam.getTemp() - entry.temp) > 0.5:
                while np.abs(self.cam.getTemp()[-1] - entry.temp) > 0.1:
                    sleep(1)
                sleep(5 * 60)  # Sleep for an additional 5min to let the chip get into an equilibrium

            if entry.type == "bias":
                if self.status != "covered":
                    input("Bias Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
                self.cam.bias()
            elif entry.type == "dark":
                if self.status != "covered":
                    input("Dark Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
            elif entry.type == "flat":
                if self.status != entry.level:
                    input("Illuminate to level: ", entry.level)
                    status = entry.level
            else:
                raise NotImplementedError("")

            print(f"Starting Capture - {datetime.now()}")
            capture(self.cam, entry.num_frames, file=f"{self.out_dir}/{entry.name}.fits")

            self.plan.loc[self.itt, 'status'] = True
            self.plan.to_csv(self.file)
            self.itt += 1



def execute_monitoring(cam):
    folder = f"data/{datetime.now():%Y%m%d}"
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(folder)

    #while True:
    print("Capturing 10 frames")
    capture(cam, 10, file=folder+'/'+f"{datetime.now():%Y%m%d_%H%M%S}"+'.fits')
    #sleep(10*60)

def execute_monitoring_loop(cam):
    folder = f"data/{datetime.now():%Y%m%d}"
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(folder)

    while True:
        print("Capturing 10 frames")
        capture(cam, 10, file=folder+'/'+f"{datetime.now():%Y%m%d_%H%M%S}"+'.fits')
        sleep(10*60)
