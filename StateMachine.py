class StateMachine:
    def __init__(self, state):
        self.state = None
        self.to_state(state)

    def create_state(self, state):
        return state(self.state)

    def process_data_point(self, data_point):
        self.state.process(self, data_point)

    def to_state(self, new_state):
        print(f"Transitioning to state {new_state.__name__}")
        self.state = self.create_state(new_state)
