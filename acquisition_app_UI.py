#!/usr/bin/python
# Author: Justin

"""
This module creates the application UI.
"""


from functools import partial
from bokeh.layouts import column, row, widgetbox, layout
from bokeh.models.widgets import Button, TextInput, Toggle, Div
from bokeh.client import push_session, pull_session, session
from bokeh.document import Document
from tornado import gen


class AcquisitionAPPUI(object):
    """AcquisitionAPP UI"""

    def __init__(self, inst_app):
        """
        Set up the connection with the Bokeh server.
        """
        self.inst_app = inst_app    # A reference to application class instance
        self.inst_app.__doc__ = Document()
        self.inst_app.__doc__.title = self.inst_app.app_name
        self.inst_app.__session__ = push_session(self.inst_app.__doc__,
                                        session_id = self.inst_app.app_name)

    def create_intro_text_bar(self, text="Introduction text", width=500):
        """
        Create a static text field displaying some introduction content.
        """
        self.intro_text_bar = Div(text=text, width=width)

    def create_ctrl_panel(self, ncols=1, width=230, height=70):
        """
        Create text box inputs for receiving pythonic strings.
        """
        self.controls = {}  # A dictionary of TextInput instances
        for key, value in self.inst_app.inputs.items():
            self.controls[key] = TextInput(value=value, title=key, width=width,
                                                        height=height)
            self.controls[key].on_change('value', self.__update_inputs__)
        for key, value in self.inst_app.parameters.items():
            self.controls[key] = TextInput(value=value, title=key, width=width,
                                                        height=height)
            self.controls[key].on_change('value', self.__update_parameters__)

        # For better viewing experience, divide to ncols columns
        tmp = list(self.controls.values())
        n_ctrls_per_col = int(len(tmp)/ncols)
        tmp_panel_list = []
        for j in range(ncols):
            start = j * n_ctrls_per_col
            end = (j + 1) * n_ctrls_per_col
            if end == len(tmp) - 1:
                end = len(tmp)
            tmp_panel_list.append(widgetbox(tmp[start:end], width=width))

        self.ctrl_panel = row(tmp_panel_list)

    def __update_inputs__(self, attrname, old, new):
        for key, value in self.controls.items():
            self.inst_app.inputs[key] = value.value

    def __update_parameters__(self, attrname, old, new):
        for key, value in self.controls.items():
            self.inst_app.parameters[key] = value.value

    def create_state_ctrls(self, btn_width=70, btn_container_width=90,
                            layout='row'):
        """
        Create state buttons: Run, Pause, Stop, Exit, etc.
        """
        btn_run = Button(label="Run", button_type="success")
        btn_run.on_click(self.on_run_handler)
        btn_pause = Toggle(label="Pause", button_type="primary")
        btn_pause.on_change('active', self.on_pause_handler)
        btn_stop = Button(label="Stop", button_type="default")
        btn_stop.on_click(self.on_stop_handler)
        btn_exit = Button(label="Exit", button_type="danger")
        btn_exit.on_click(self.on_exit_handler)
        tmp = []
        for btn in [btn_run, btn_pause, btn_stop, btn_exit]:
            btn.width = btn_width
            tmp.append(widgetbox(btn, width = btn_container_width))
        if layout == 'row':
            self.state_ctrls = row(tmp)
        else:
            self.state_ctrls = column(tmp)


    def create_status_bar(self, status_bar_width=600):
        """
        Add a dynamic text field displaying the system status. A periodic
        callback is added to keep its value updated
        """
        self.status_bar = Div(text="", width = status_bar_width)
        self.inst_app.__doc__.add_periodic_callback(
                                    self.__update_status_bar__, 150)

    @gen.coroutine
    def __update_status_bar__(self):
        """Update the status bar"""
        tmp = "<p><i>State: {}</i><p><p>{}<p>".format(
                    self.inst_app.__state_name__, self.inst_app.__message__)
        self.status_bar.text = tmp

    def create_UI(self):
        """
        Create the UI.

        Note: the figures are created using the function in the application
        class.

        Structure:
        ---intro_text_bar---
        ctrl_panel   figs
        state_ctrls
        status_bar
        """
        self.create_intro_text_bar(text=self.inst_app.intro_text)
        self.create_ctrl_panel(ncols=self.inst_app.ctrl_panel_ncols)
        self.create_state_ctrls()
        self.create_status_bar()

        # Create figs using applicatio class function
        figs = self.inst_app.create_figs()

        UI = layout([
                        [self.intro_text_bar],
                        [self.ctrl_panel, figs],
                        [self.state_ctrls],
                        [self.status_bar]
                    ])

        self.inst_app.__doc__.add_root(UI)
        # Open the document in a browser
        # self.inst_app.__session__.show(browser=self.inst_app.browser)
        self.inst_app.__session__.loop_until_closed() # run forever

    # Event handlers
    def __reset_state__(self):
        self.inst_app.__run_request__ = False
        self.inst_app.__stop_request__ = False
        self.inst_app.__exit_request__ = False

    def on_run_handler(self):
        self.__reset_state__()
        self.inst_app.__run_request__ = True

    def on_pause_handler(self, attr, old, new):
        # Toggle on/off for pause
        self.__reset_state__()
        self.inst_app.__pause_request__ = not self.inst_app.__pause_request__

    def on_stop_handler(self):
        self.__reset_state__()
        self.inst_app.__stop_request__ = True

    def on_exit_handler(self):
        self.__reset_state__()
        self.inst_app.__exit_request__ = True


if __name__ == '__main__':
    inst_acq_app_UI = AcquisitionAPPUI("test_app")
    inst_acq_app_UI.create_UI()
