from SimpleAgent import SimpleAgent
from Resource import Resource

class StateBasedAgent(SimpleAgent):
    EXPLORED = True
    UNEXPLORED = False
    
    def __init__(self, model):
        super().__init__(model)
        self.explored = dict() # Dicionario que mapeia um par ordenado em -> Explorado/Não Explorado
        self.type = "StateBasedAgent"
        self.color = "red"
        self.shape = "triangle"

    def move(self):
        self.explored[self.pos] = self.EXPLORED
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        unexplored_steps = []
        for step in possible_steps:
            if self.explored.get(step) is None and step not in self.model.obstacles:
                unexplored_steps.append(step)

        if len(unexplored_steps) > 0:
            new_position = self.random.choice(unexplored_steps)
        else:
            new_position = self.random.choice(possible_steps)
            while new_position in self.model.obstacles:
                new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)


    @property
    def color(self):
        return self._color

    @property
    def shape(self):
        return self._shape
    
    @shape.setter
    def shape(self, value):
        self._shape = value
    
    @color.setter
    def color(self, value):
        self._color = value