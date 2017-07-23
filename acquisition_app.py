#!/usr/bin/python
# Author: Justin


"""
This module defines an appliation class named AcquisitionAPP for data
acquisition.

Note this class is a full-fledged demo application. In order to create a custom 
application, one needs to inherit this class and override the following
attributes and methods:

    self.app_name           # Application name. This parameter is used to
                            # create application URL
    self.inputs             # Application inputs. Should be in the form of
                            # {'input_str': 'pythonic_string' ...}
    self.parameters         # Other parameters. Should be in the form of
                            # {'input_str': 'pythonic_string' ...}
    self.empty_data         # Used to tell the program how the empty outputs
                            # look like. It should be of the form:
                            # {'input_str': [], ... 'output_str': [] ...}
    self.intro_text         # Static HTML text to be displayed. Used for
                            # showing the name and purpose of the
                            # application
    def config(self):       # Things to do during program initialization.
                            # Note this method runs only once after the
                            # program starts
    def acquire(self):      # Acqusition body
    def save(self):         # Things to do when acqusition stops, e.g.,
                            # saving data
    def exit(self):         # Things to do when exiting the application
    def create_figs(self):  # Method to create Bokeh figures

In addition, to assist application development, the following UI events
related parameters can be used with flexibility:

    self.__run_request__    # Request to start the acqusition. Equivalent to
                            # pressing the Run button
    self.__just_started__   # Set True right after the acquisition starts. It's
                            # useful when some specific operations are needed
                            # at the very initial stage of acquisition. It
                            # should be set to False when the specific 
                            # operations are completed
    self.__pause_request__  # Request to pause the application
    self.__stop_request__   # Request to stop the application
    self.__exit_request__   # Request to exit the application
"""


from __future__ import print_function
from threading import Thread
from bokeh.models import ColumnDataSource
from acquisition_app_UI import AcquisitionAPPUI
from acquisition_app_statemachine import AcquisitionAPPStateMachine
import copy
import numpy as np
import time
import sys


class AcquisitionAPP(object):
    """
    Create a simple browser-based data acquisition application.

    This application replies on Bokeh for interactive data plottig.

    This application comprises of two modules: the state machine module is
    reponsible for run/pause/stop/exit UI events; the UI module is responsible
    for creating the browser interface and data plotting. The module run in
    their own thread and share the data via a few global variables.

    The philosophy is we measure the response (outputs) for given inputs at
    a certain conditions (parameters). In order to take advantage of the full
    flexibility of Python, the values of both inputs and parameters are in the
    form of pythonic strings, i.e., you can use np.linspace to readily generate
    a list input instead of three separate inputs for start, stop, and step.
    """

    def __init__(self, app_name):
        """
        Define a few application level parameters.

        inputs and parameters together define the controls of application. The
        inputs denote the independent variables to be studied and are generally
        of type list (np.array). The parameters are the static controls and do
        not change during each single acquisition process.  Both inputs and
        parameters are dictionary type. To take advantage of Python, the values
        of both dictionaries are pythsonic strings.

        outputs and empty_data define the application outcomes. The keys of
        empty_data should be consistent with inputs and outputs. outputs must
        be a Bokeh.ColumnDataSource in order for plot functions to work
        properly.
        """
        if ' ' in app_name:
            sys.exit("Error: The name of the application is used to create URL"
                                ", thus no whitespace is allowed")
        self.app_name = app_name

        # Key parameters for defining the acquasition
        self.inputs = { 'x1': 'np.linspace(0,1,100)',
                        'x2': 'np.linspace(0,1,100)'}
        self.parameters = { 'S1': '12.3', 'S2': "'haha'", 'S3':'[1,2]',
                            'S4':'np.array([3,4])', 'S5':'{}'}
        self.empty_data = {'x1': [], 'x2': [], 'y1': [], 'y2': []}

        # Browser for showing the application
        self.browser = 'windows-default'    # Not used if running via Flask

        # Introduction text above the plots
        self.intro_text = "<font size='5'><b>{}</b></font>".format(app_name)

        # Cosmetics for the contrl panel
        self.ctrl_panel_ncols = 1       # Number of columns

        # State control and status bar related variables
        self.__state_name__ = None
        self.__message__ = ""

        # UI events related variables
        self.__run_request__ = False
        self.__just_started__ = False
        self.__pause_request__ = False
        self.__stop_request__ = False
        self.__exit_request__ = False

        # Bokeh server related variables
        self.__doc__ = None
        self.__session__ = None

    def config(self):
        """
        Configuring the instrument during the Initialization state.
        """
        print("Program configuration")

    def acquire(self):
        """
        Data acquisition during the Run state.

        Note: at the very beginning (self.__just_started__ == True), one may
        need to initialize the inputs.

        Note: set "self.__stop_request__ = True" at the end of the acqusition.
        This tells the state machine to jump out of the Run state.

        For simple-step acquisition, set the __stop_request__ flag at the end of
        this function. For streaming acquisition, use a global counter and set
        the flag when the counter reaches desired value.

        In order to be successfully appended to the outputs (which is in the
        form of ColumnDataSource, the return value must be a dictionary.

        Need to return None in case of errors.
        """

        # The following code is good for single-step acquisition
        """
        time.sleep(2)
        x1 = self.__exec__(self.inputs['x1'])
        x2 = self.__exec__(self.inputs['x2'])
        if x1 is None or self.x2 is None:
            return

        y1 = np.sin(x1)
        y2 = np.cos(x2)
        self.__stop_request__ = True     # Equivalent to pressing the stop button
        data = {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2}
        return data
        """

        # The following code is good for streaming acquisition
        if self.__just_started__:
            # Things to do at the first Run state, such as initializing the
            # inputs
            self.x1 = self.__exec__(self.inputs['x1'])
            self.x2 = self.__exec__(self.inputs['x2'])
            if self.x1 is None or self.x2 is None:
                return
            self.count = 0
            self.length = len(self.x1)
            if self.length != len(self.x2):
                # Two inputs are of different lengths
                error_message = "Two inputs are of different lengths"
                # Append message
                self.__message__ += "<p><font color='red'>Error: {}</font><p>".format(
                                error_message)
                return
            self.__just_started__ = False
        x1_single = self.x1[self.count]
        x2_single = self.x2[self.count]
        y1_single = np.sin(x1_single)
        y2_single = np.cos(x2_single)
        if self.count == self.length - 1:
            self.__stop_request__ = True     # Equivalent to pressing the stop button
        else:
            self.count = self.count + 1
            time.sleep(0.2)
        data = {'x1': x1_single, 'x2': x2_single, 'y1': y1_single, 'y2': y2_single}
        return data

    def save(self):
        """
        Things to do when the Stop state has been reached.
        """
        print("Saving data")


    def exit(self):
        """
        Things to do when the Exit state has been reached.
        """
        print("Exiting program")

    def create_figs(self):
        """
        Create bokeh figures. There shouldn't be problem using any types of
        bokeh plots. Just remember to import the required modules at the
        beginning.
        """
        from bokeh.models.widgets import Panel, Tabs
        from bokeh.plotting import figure
        fig1 = figure(tools="pan, lasso_select, box_select, tap, wheel_zoom,"
                            " box_zoom, crosshair, hover, resize, reset",
                            plot_width=600, plot_height=400)
        fig1.circle(x='x1', y='y1', source=self.outputs)
        fig1.xaxis.axis_label = "x1"
        fig1.yaxis.axis_label = "y1"
        tab1 = Panel(child=fig1, title="y1 vs x1")

        fig2 = figure(tools="pan, lasso_select, box_select, tap, wheel_zoom,"
                            " box_zoom, crosshair, hover, resize, reset",
                            plot_width=600, plot_height=400)
        fig2.circle(x='x2', y='y2', source=self.outputs)
        fig2.xaxis.axis_label = "x2"
        fig2.yaxis.axis_label = "y2"
        tab2 = Panel(child=fig2, title="y2 vs x2")

        tabs = Tabs(tabs=[tab1, tab2])
        return tabs

    def __exec__(self, string):
        """
        Try to execuate the pythonic string command and produce a message in
        case of errors.

        Return None if a error is detected.
        """
        rlt = None
        try:
            # exec is more versatile than eval. It accepts multi-line pythonic
            # strings but has no return
            ldict = locals()
            exec("rlt = " + string, globals(), ldict)
            rlt = ldict['rlt']
        except:
            error_message = "Pythonic string '{}' cannot be execuated.".format(
                            string)
            # Append message
            self.__message__ += "<p><font color='red'>Error: {}</font><p>".format(
                            error_message)
            return
        else:
            return rlt

    def run(self, app_name="acquisition_app"):
        """
        Run the application.

        Two threads will be created: one for UI and the other for state machine.
        """
        self.outputs = ColumnDataSource(copy.deepcopy(self.empty_data))
        inst_acq_app_UI = AcquisitionAPPUI(self)
        inst_acq_app_SM = AcquisitionAPPStateMachine(self)
        thread_UI = Thread(target=inst_acq_app_UI.create_UI)
        thread_UI.start()
        thread_SM = Thread(target=inst_acq_app_SM.runAll)
        thread_SM.start()


if __name__ == '__main__':
    inst_acq_app = AcquisitionAPP(app_name="acquisition_app")
    inst_acq_app.run()
