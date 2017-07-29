#!/usr/bin/python
# Author: Justin


"""
This module creates two example Bokeh + Flask applications that run in parallel.
"""


from acquisition_app import AcquisitionAPP
import time
import webbrowser
import pandas as pd
import numpy as np
from bokeh.plotting import figure

class RvsH(AcquisitionAPP):
    """
    A simple acqusition demo.

    This application sends the inputs to the instrument and wait for response
    to arrive in one piece.
    """
    def __init__(self, app_name):
        super(RvsH, self).__init__(app_name)
        # Key parameters, such as inputs, parameters, and how empty_data looks
        # like
        self.inputs = {'Field (Oe)': 'np.linspace(0, 10, 100)'}
        self.parameters = { 'Source amplitude': '1e-3', 'Source type': 'I',
                            'Save path': 'd:/RvsH.csv'}
        self.empty_data = {'Field (Oe)': [], 'Resistance (Ohm)': []}

    def config(self):
        print("Program configuration")

    def acquire(self):
        # Single aquisition
        field = self.__exec__(self.inputs['Field (Oe)'])
        if field is None:
            return

        time.sleep(2)               # Fake acquisition wait time
        self.__just_started__ = False

        resistance = np.sin(field)  # Fake data
        self.__stop_request__ = True     # Equivalent to pressing the stop button
        data = {'Field (Oe)': field, 'Resistance (Ohm)': resistance}
        return data

    def save(self):
        print("Saving data")
        tmp = self.outputs.to_df()
        try:
            tmp.to_csv(self.parameters['Save path'])
        except:
            error_message = "File cannot be saved!"
            # Append message
            self.__message__ += "<p><font color='red'>Error: {}</font><p>".format(
                            error_message)

    def exit(self):
        print("Exiting program")

    def create_figs(self):
        # Create the figure
        fig = figure(tools="pan, lasso_select, box_select, tap, wheel_zoom,"
                            " box_zoom, crosshair, hover, resize, reset",
                            plot_width=600, plot_height=400)
        fig.circle(x='Field (Oe)', y='Resistance (Ohm)', source=self.outputs)
        fig.xaxis.axis_label = "Field (Oe)"
        fig.yaxis.axis_label = "Resistance (Ohm)"

        return fig

class ErrRatevsVolt(AcquisitionAPP):
    """
    Streaming data acqusition demo.

    This application supplies the instrument with a single input one per
    acqusition cycle. The result is immediately measured and plotted in real
    time.
    """
    def __init__(self, app_name):
        super(ErrRatevsVolt, self).__init__(app_name)
        # Key parameters, such as inputs, parameters, and how empty_data looks
        # like
        self.inputs = {'Volt (V)': 'np.linspace(-1, 1, 100)'}
        self.parameters = { 'Read bias (V)': '0.1',
                            'Pulse width (ns)': '[1, 10, 100]',
                            'Applied field': 'True',
                            'Save path': 'd:/ErrRatevsVolt.csv'}
        self.empty_data = { 'Volt (V)': [],
                            'Error rate': [],
                            '1 - Error rate': [],
                            'Pulse width (ns)': [],
                            'Applied field': [],
                            'color': []}
        self.pw_idx = 0

    def config(self):
        print("Program configuration")

    def acquire(self):
        # Acquisition with streamingd data
        if self.__just_started__:
            # Things to do at the very first acquisition cycle, such as
            # initializing inputs, etc.
            self.pw = self.__exec__(self.parameters['Pulse width (ns)'])
            self.voltage = self.__exec__(self.inputs['Volt (V)'])
            if self.voltage is None or self.pw is None:
                return
            self.pw_idx = 0
            self.voltage_idx = 0
            # Record the number of pulse witdhs and voltages
            self.n_pw = len(self.pw)
            self.n_voltage = len(self.voltage)
            self.color_list = ['red', 'green', 'blue', 'yellow', 'navy']
            # Reset the flag
            self.__just_started__ = False

        voltage_single = self.voltage[self.voltage_idx]
        pw_single = self.pw[self.pw_idx]
        # Fake data
        errrate1_single = np.piecewise(voltage_single,
                                    [voltage_single < 0, voltage_single >= 0],
                                    [lambda x: (np.tanh(20 * x + 0.5) + 1) / 2,
                                     lambda x: (np.tanh(0.5 - 20 * x) + 1) / 2])
        errrate1_single = errrate1_single / pw_single
        errrate2_single = 1 - errrate1_single
        time.sleep(0.05)                    # Fake acquisition wait time
        data = {'Volt (V)': voltage_single, 'Error rate': errrate1_single,
                '1 - Error rate': errrate2_single, 'Pulse width (ns)': pw_single,
                'Applied field': 1 if self.parameters['Applied field'] == 'True' else 0,
                'color': self.color_list[self.pw_idx]}

        # Increase the indices for the next acqusition cycle
        if self.pw_idx == self.n_pw - 1 and self.voltage_idx == self.n_voltage - 1:
            self.__stop_request__ = True    # Done with acqusition
        else:
            if self.voltage_idx == self.n_voltage - 1:
                self.voltage_idx = 0
                time.sleep(1)
                print("Done with all voltages. Switch to next pulse width")
                self.pw_idx += 1
            else:
                self.voltage_idx += 1

        return data

    def save(self):
        print("Saving data")
        tmp = self.outputs.to_df()
        try:
            tmp.to_csv(self.parameters['Save path'])
        except:
            error_message = "File cannot be saved!"
            # Append message
            self.__message__ += "<p><font color='red'>Error: {}</font><p>".format(
                            error_message)

    def exit(self):
        print("Exiting program")

    def create_figs(self):
        # Create two figures and put each in its own tabs
        from bokeh.models.widgets import Panel, Tabs
        from bokeh.plotting import figure
        fig1 = figure(tools="pan, lasso_select, box_select, tap, wheel_zoom,"
                            " box_zoom, crosshair, hover, resize, reset",
                            plot_width=600, plot_height=400, y_axis_type="log")
        fig1.circle(x='Volt (V)', y='Error rate', source=self.outputs,
                                        color='color')
        fig1.xaxis.axis_label = "Volt (V)"
        fig1.yaxis.axis_label = "Error rate"
        fig1.background_fill_color = "beige"
        tab1 = Panel(child=fig1, title="Error rate vs Volt (V)")

        fig2 = figure(tools="pan, lasso_select, box_select, tap, wheel_zoom,"
                            " box_zoom, crosshair, hover, resize, reset",
                            plot_width=600, plot_height=400, y_axis_type="log")
        fig2.circle(x='Volt (V)', y='1 - Error rate', source=self.outputs,
                                        color='color')
        fig2.xaxis.axis_label = "Volt (V)"
        fig2.yaxis.axis_label = "1 - Error rate"
        fig2.background_fill_color = "beige"
        tab2 = Panel(child=fig2, title="1 - Error rate vs Volt (V)")

        # Return the tabs
        tabs = Tabs(tabs=[tab1, tab2])
        return tabs


if __name__ == '__main__':
    app_name_list = list()

    # Create two applications
    app_name = 'R_vs_H'
    app_name_list.append(app_name)
    RvsH(app_name=app_name).run()

    app_name = 'ErrRate_vs_Volt'
    app_name_list.append(app_name)
    ErrRatevsVolt(app_name=app_name).run()

    # Open each applications in new tabs in chrome
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    for app_name in app_name_list:
        webbrowser.get(chrome_path).open("http://localhost:5000/{}".format(app_name))
