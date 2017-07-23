#!/usr/bin/python
# Author: Justin

"""
This module asserts two abstract classes for state machine application.
"""

class State(object):
    """Template class State"""
    def run(self):
        assert False, "State.run() not implemented!"
    def next(self):
        assert False, "State.next() not implemented!"

class StateMachine(object):
    """Template class StateMachine"""
    def __init__(self, initial_state):
        """Initialize a state machine. The initial state is added."""
        print("StateMachine starts running ...")
        self.curr_state = initial_state

    def runAll(self):
        """Run all states"""
        while self.curr_state is not None:
            self.curr_state.run()
            self.curr_state = self.curr_state.next()
        print("StateMachine has terminated.")
