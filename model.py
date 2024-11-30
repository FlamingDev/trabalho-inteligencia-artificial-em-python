import random

import mesa

class SimpleAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.collected_resources = 0
        self.score = 0
        self.has_resource = False

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)

        new_position = self.random.choice(possible_steps)
        while new_position in self.model.obstacles:
            new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)

    def collect_resource_if_present(self):
        if not self.has_resource:
            cell_contents = self.model.grid.get_cell_list_contents(self.pos)
            for obj in cell_contents:
                if isinstance(obj, Resource):
                    if obj.size != obj.HEAVY:
                        self.has_resource = True
                        self.model.grid.remove_agent(obj)
                        return

    def go_back_to_base(self):
        if self.has_resource:
            current_x, current_y = self.pos
            destination_x, destination_y = self.model.base_pos
            next_x = current_x + (1 if destination_x > current_x else -1 if destination_x < current_x else 0)
            next_y = current_y + (1 if destination_y > current_y else -1 if destination_y < current_y else 0)

            next_pos = (next_x, next_y)

            if next_pos not in self.model.obstacles:
                self.model.grid.move_agent(self, next_pos)
            else:
                self.move()

    def is_at_base(self):
        return self.pos == self.model.base_pos

    def deliver_resource(self):
        if self.has_resource and self.is_at_base():
            self.collected_resources += 1
            self.has_resource = False

    def step(self):
        self.collect_resource_if_present()
        if self.has_resource:
            self.go_back_to_base()
            self.deliver_resource()
        else:
            self.move()

class StateBasedAgent(SimpleAgent):
    UNEXPLORED = 0
    EXPLORED = 1
    def __init__(self, model):
        super().__init__(model)
        self.explored = dict()

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


class ObjectiveBasedAgent(StateBasedAgent):
    def __init__(self, model):
        super().__init__(model)
        self.known_resources = list()
        self.next_objective = None

    def collect_resource_if_present(self):
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if isinstance(obj, Resource):
                if not self.has_resource and obj.size != obj.HEAVY:
                    self.has_resource = True
                    self.model.grid.remove_agent(obj)
                elif self.pos not in self.known_resources and obj.size != obj.HEAVY:
                    self.known_resources.append(self.pos)

    def deliver_resource(self):
        if self.has_resource and self.is_at_base():
            self.collected_resources += 1
            self.has_resource = False
            if len(self.known_resources) > 0:
                self.next_objective = self.known_resources.pop()
            else:
                self.next_objective = None

    def go_to_next_objective(self):
        current_x, current_y = self.pos
        destination_x, destination_y = self.next_objective
        next_x = current_x + (1 if destination_x > current_x else -1 if destination_x < current_x else 0)
        next_y = current_y + (1 if destination_y > current_y else -1 if destination_y < current_y else 0)

        next_pos = (next_x, next_y)

        if next_pos == self.pos:
            self.next_objective = None


        if next_pos not in self.model.obstacles:
            self.model.grid.move_agent(self, next_pos)
        else:
            self.move()


    def step(self):
        self.collect_resource_if_present()
        if self.has_resource:
            self.go_back_to_base()
            self.deliver_resource()
        else:
            if self.next_objective is not None:
                print(f"{self.unique_id } TEM UM OBJETIVO AGORA")
                self.go_to_next_objective()
            else:
                self.move()

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
    def __init__(self, n_SA,
                 n_SBA, n_OBA, height, width, n_resources , n_obstacles=0, base_pos = (0,0), seed=None):
        super().__init__(seed=seed)
        self.n_SA = n_SA
        self.n_SBA = n_SBA
        self.n_OBA = n_OBA
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

            if (x,y) != base_pos:
                self.grid.place_agent(Obstacle(self), (x,y))
                self.obstacles.append((x,y))

        for _ in range(n_SA):
            a = SimpleAgent(self)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_SBA):
            a = StateBasedAgent(self)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_OBA):
            a = ObjectiveBasedAgent(self)
            self.grid.place_agent(a, base_pos)

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
                            if obj.size == obj.SMALL:
                                print(f"{RED}SR{RESET}  ", end="")
                            elif obj.size == obj.MEDIUM:
                                print(f"{RED}MR{RESET}  ", end="")
                            elif obj.size == obj.HEAVY:
                                print(f"{RED}HR{RESET}  ", end="")
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
                agent.step()