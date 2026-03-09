class AgentState:

    def __init__(self, goal):

        self.goal = goal
        self.plan = []
        self.current_step = 0

        self.action_history = []
        self.failure_count = 0

        self.success = False

    def set_plan(self, plan):

        self.plan = plan
        self.current_step = 0

    def next_step(self):

        if self.current_step >= len(self.plan):
            return None

        step = self.plan[self.current_step]

        self.current_step += 1

        return step

    def remember_action(self, action):

        self.action_history.append(action)

        if len(self.action_history) > 10:
            self.action_history.pop(0)

    def detect_loop(self, action):

        if len(self.action_history) < 2:
            return False

        if action == self.action_history[-1] == self.action_history[-2]:
            return True

        return False

    def register_failure(self):

        self.failure_count += 1

    def reset_failures(self):

        self.failure_count = 0

    def too_many_failures(self):

        return self.failure_count >= 3