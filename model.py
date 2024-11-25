import mesa

class SimpleAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.collected_resources = 0
        self.score = 0
        self.hasResource = False

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def collect_resource(self):
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if isinstance(obj, Resource):
                self.hasResource = True
                self.collected_resources += 1
                self.model.grid.remove_agent(obj)

    def get_back_to_base(self):


class Resource(mesa.Agent):
    SMALL = 0
    MEDIUM = 1
    HEAVY = 2

    def __init__(self, size, model):
        super().__init__(model)
        self.size = size
        if size == self.SMALL:
            self.utility = 10
        elif size == self.MEDIUM:
            self.utility = 20
        else:
            self.utility = 50

class Obstacle(mesa.Agent):

    def __init__(self, model):
        super().__init__(model)

class Planet(mesa.Model):
    def __init__(self, n_agents , height, width, n_resources , n_obstacles):
        super().__init__()
        self.NumAgents = n_agents
        self.grid = mesa.space.MultiGrid(height,width, torus=False)
        self.basePos = (0,0)

        for _ in range(n_resources):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            size = self.random.choice([Resource.SMALL, Resource.MEDIUM, Resource.HEAVY])
            self.grid.place_agent(Resource(size,self), (x,y))

        for _ in range(n_obstacles):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            self.grid.place_agent(Obstacle(self), (x,y))

        for _ in range(n_agents):
            self.grid.place_agent(SimpleAgent(self), self.basePos)

    def show_grid(self):
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents((i, j))
                print(f"{i, j} ", end="")
                if len(cell_contents) > 0:
                    for obj in cell_contents:
                        if isinstance(obj, Resource):
                            print("R  ", end="")
                        elif isinstance(obj, Obstacle):
                            print("O  ", end="")
                        elif isinstance(obj, SimpleAgent):
                            print("A  ", end="")
                        else:
                            print("X  ", end="")
                else:
                    print("X  ", end="")

            print()

    def step(self):
        for agent in self.agents:
            if isinstance(agent, SimpleAgent):
                agent.move()
                agent.collect_resource()