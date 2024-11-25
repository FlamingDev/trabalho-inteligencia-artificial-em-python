import mesa
from mesa.time import RandomActivation


class SimpleAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.collected_resources = 0
        self.score = 0
        self.has_resource = False

    def move_randomly(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)

        new_position = self.random.choice(possible_steps)
        while new_position in self.model.obstacles:
            new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)

    def collect_resource(self):
        if not self.has_resource:
            cell_contents = self.model.grid.get_cell_list_contents(self.pos)
            for obj in cell_contents:
                if isinstance(obj, Resource):
                    self.has_resource = True
                    self.model.grid.remove_agent(obj)
                    break

    def get_back_to_base(self):
        if self.has_resource:
            current_x, current_y = self.pos
            base_x, base_y = self.model.base_pos
            next_x = current_x + (1 if base_x > current_x else -1 if base_x < current_x else 0)
            next_y = current_y + (1 if base_y > current_y else -1 if base_y < current_y else 0)

            next_pos = (next_x, next_y)

            if next_pos not in self.model.obstacles:
                self.model.grid.move_agent(self, next_pos)
            else:
                (self.move_randomly())

    def is_at_base(self):
        return self.pos == self.model.base_pos;

    def deliver_resource(self):
        if (self.has_resource and self.pos == self.model.base_pos):
            self.collected_resources += 1
            self.has_resource = False

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
    def __init__(self, n_agents , height, width, n_resources , n_obstacles, base_pos = (0,0), seed=None):
        super().__init__(seed=seed)
        self.NumAgents = n_agents
        self.obstacles = []
        self.grid = mesa.space.MultiGrid(height,width, torus=False)
        self.base_pos = base_pos

        for _ in range(n_resources):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            size = self.random.choice([Resource.SMALL, Resource.MEDIUM, Resource.HEAVY])
            self.grid.place_agent(Resource(size,self), (x,y))

        for _ in range(n_obstacles):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            if (x,y) != (0,0):
                self.grid.place_agent(Obstacle(self), (x,y))
                self.obstacles.append((x,y))

        for _ in range(n_agents):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            a = SimpleAgent(self)
            self.grid.place_agent(a, base_pos)
            #self.schedule.add(a)

    def show_grid(self):
        GREEN = "\033[92m"
        BLUE = "\033[94m"
        RESET = "\033[0m"
        RED = "\033[91m"

        for i in range(self.grid.width):
            for j in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents((i, j))
                print(f"{i, j} ", end="")
                if len(cell_contents) > 0:
                    for obj in cell_contents:
                        if isinstance(obj, Resource):
                            print(f"{RED}R{RESET}  ", end="")
                        elif isinstance(obj, Obstacle):
                            print("O  ", end="")
                        elif isinstance(obj, SimpleAgent):
                            if obj.has_resource:
                                print(f"{BLUE}{obj.unique_id}{RESET}  ", end="")
                            else:
                                print(f"{GREEN}{obj.unique_id}{RESET}  ", end="")
                        else:
                            print("X  ", end="")
                else:
                    print("X  ", end="")

            print()

    def step(self):
        for agent in self.agents:
            if isinstance(agent, SimpleAgent):
                agent.collect_resource()
                if agent.has_resource:
                    agent.get_back_to_base()
                    agent.deliver_resource()
                else:
                    agent.move_randomly()