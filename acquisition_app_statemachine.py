#!/usr/bin/python
# Author: Justin

"""
This module defines the application state machine.

Five states have been defined:
Initialization:     Good for configuring instrument. It runs only once at the
                    very beginning
Idle:               Waiting for inputs
Run:                Take measurement. This state runs indefinitely until a
                    __stop_request__ is issued
Stop:               The target state after a __stop_request__ is issued. Good
                    for saving data
Exit:               Reset the instrument, close any open sessions, and exit the
                    program safely
"""


from __future__ import print_function
from statemachine import State, StateMachine
from random import random
from tornado import gen
from bokeh.models import ColumnDataSource
from functools import partial
from threading import Lock
import time
import copy


class Initialization(State):
    """State - Initialization"""
    __state_name__ = "Initialization"

    def __init__(self, inst_sm):
        self.inst_sm = inst_sm
        self.inst_app = inst_sm.inst_app    # A reference to application class instance

    def run(self):
        self.inst_app.__state_name__ = self.__state_name__
        ### Things to do during Initialization state, e.g., instrument configuration ###
        self.inst_app.config()
        ################################################################################
    def next(self):
        return self.inst_sm.idle

class Idle(State):
    """State - Idle"""
    __state_name__ = "Idle"

    def __init__(self, inst_sm):
        self.inst_sm = inst_sm
        self.inst_app = inst_sm.inst_app    # A reference to application class instance

    def run(self):
        self.inst_app.__state_name__ = self.__state_name__
        time.sleep(0.2)
    def next(self):
        if self.inst_app.__exit_request__ == True:
            self.inst_app.__exit_request__ = False
            return self.inst_sm.exit
        elif self.inst_app.__run_request__ == True:
            self.inst_app.__run_request__ = False
            self.inst_app.__just_started__ = True
            # Reset data
            self.inst_app.outputs.data = copy.deepcopy(self.inst_app.empty_data)
            self.inst_app.__message__ = ""
            return self.inst_sm.run
        else:
            return self.inst_sm.idle

class Run(State):
    """State - Run"""
    __state_name__ = "Run"

    def __init__(self, inst_sm):
        self.inst_sm = inst_sm
        self.inst_app = inst_sm.inst_app    # A reference to application class instance

    def run(self):
        # Pause request
        if self.inst_app.__pause_request__:
            self.inst_app.__state_name__ = "Pause"
        while self.inst_app.__pause_request__:
            time.sleep(0.2)
        self.inst_app.__state_name__ = self.__state_name__
        ### Things to do during the Run state, e.g., computation, measurement, etc. ###
        AcquisitionAPPStateMachine.__acquire__(self.inst_app)
        ###############################################################################
    def next(self):
        if self.inst_app.__stop_request__ == True:
            self.inst_app.__stop_request__ = False
            return self.inst_sm.stop
        else:
            return self.inst_sm.run

class Stop(State):
    """State - Stop"""
    __state_name__ = "Stop"

    def __init__(self, inst_sm):
        self.inst_sm = inst_sm
        self.inst_app = inst_sm.inst_app    # A reference to application class instance

    def run(self):
        self.inst_app.__state_name__ = self.__state_name__
        ### Things to do during the Stop state, e.g., stopping equipment, saving data ###
        if not self.inst_app.__just_started__:
            # Don't save if the program just started
            self.inst_app.save()
        else:
            self.inst_app.__just_started__ = not self.inst_app.__just_started__
        #################################################################################
    def next(self):
        return self.inst_sm.idle


class Exit(State):
    """State - Exit"""
    __state_name__ = "Exit"

    def __init__(self, inst_sm):
        self.inst_sm = inst_sm
        self.inst_app = inst_sm.inst_app    # A reference to application class instance

    def run(self):
        self.inst_app.__state_name__ = self.__state_name__
        ### Things to do during the Exit state, e.g., equipment reset ###
        time.sleep(1)
        self.inst_app.__session__.close()   # Close Bokeh session
        self.inst_app.exit()
        #################################################################
    def next(self):
        return None

class AcquisitionAPPStateMachine(StateMachine):
    """AcquisitionAPP StateMachine"""
    def __init__(self, inst_app):
        self.inst_app = inst_app    # A reference to application class instance

        # Should not use static class variables since self is
        # passed as argument!!!
        self.initialization = Initialization(self)
        self.idle = Idle(self)
        self.run = Run(self)
        self.stop = Stop(self)
        self.exit = Exit(self)
        super(AcquisitionAPPStateMachine, self).__init__(self.initialization)

    @staticmethod
    @gen.coroutine
    def __update__(inst_app, new_data):
        """Append new data to the outputs"""
        inst_app.outputs.stream(new_data)

    @staticmethod
    def __acquire__(inst_app):
        new_data = inst_app.acquire()
        if new_data is None:
            inst_app.__stop_request__ = True    # Escape Run state
            return
        if type(new_data) is not dict:
            # Append message variable from the application instance
            inst_app.__message__ += "<p><font color='red'>Error: {}</font><p>".format(
                            "acquire() needs to return a dictionary ")
            inst_app.__stop_request__ = True    # Escpate Run state
            return
        for key, value in new_data.items():
            # Make sure key is str and value is iterable
            if type(key) is not str:
                new_key = str(key)
                new_data[new_key] = new_data[key]
                del new_data[key]
            if not hasattr(value, '__iter__'):
                new_data[key] = [value]
        inst_app.__doc__.add_next_tick_callback(partial(
                                    AcquisitionAPPStateMachine.__update__,
                                    inst_app=inst_app, new_data=new_data))


if __name__ == '__main__':
    inst_acq_app_SM = AcquisitionAPPStateMachine()
    inst_acq_app_SM.runAll()
