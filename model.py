import random

import mesa

class SimpleAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.collected_resources = 0
        self.score = 0
        self.has_resource = False
        self.current_resource = None

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
                        self.current_resource = obj
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
            self.score += self.current_resource.utility
            self.has_resource = False
            self.current_resource = None

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
                    self.current_resource = obj
                    self.model.grid.remove_agent(obj)
                elif self.pos not in self.known_resources and obj.size != obj.HEAVY:
                    print(f" {self.unique_id} está EMPILHANDO MEMORIA")
                    self.known_resources.append(self.pos)

    def deliver_resource(self):
        if self.has_resource and self.is_at_base():
            if self.current_resource is not None:
                self.collected_resources += 1
                self.score += self.current_resource.utility
            self.current_resource = None
            self.has_resource = False

    def get_next_objective(self):
        if len(self.known_resources) > 0:
            self.next_objective = self.known_resources.pop()
        else:
            print(f"{self.unique_id} nao tem mais um objetivo...")
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
            if self.is_at_base():
                self.get_next_objective()
        else:
            if self.next_objective is not None:
                print(f"{self.unique_id } TEM UM OBJETIVO AGORA")
                self.go_to_next_objective()
            else:
                self.move()


def calculate_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class CooperativeAgent(ObjectiveBasedAgent):
    def __init__(self, model):
        super().__init__(model)
        self.blocked = False
        self.help_requests = set()

    def collect_resource_if_present(self):
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if isinstance(obj, Resource):
                if not self.has_resource and obj.size != obj.HEAVY:
                    self.has_resource = True
                    self.current_resource = obj
                    self.model.grid.remove_agent(obj)
                elif self.pos not in self.known_resources and obj.size != obj.HEAVY:
                    self.known_resources.append(self.pos)

                else:
                    other_agent = next(
                        (agent for agent in cell_contents if isinstance(agent, CooperativeAgent) and agent != self), None)
                    if other_agent:
                        self.has_resource = True
                        self.current_resource = obj
                        other_agent.has_resource = True
                        self.model.grid.remove_agent(obj)
                        print(f"{self.unique_id} e {other_agent.unique_id} estão compartilhando o recurso!")


    def ask_for_help(self, target_resource):
        for agent in self.model.agents:
            if isinstance(agent, CooperativeAgent) and agent != self:
                agent.help_requests.add(target_resource)

    def respond_to_request(self):
        for request in self.help_requests:
            resource_pos = request
            if calculate_distance(self.pos, resource_pos) <= 2:
                self.help_requests.remove(request)
                print(f"Agent {self.unique_id} decided to help the agent at {resource_pos}!")
                return resource_pos
            else:
                print(f"Agent {self.unique_id} declined the help request at {resource_pos}.")
        return None

    def step(self):
        self.collect_resource_if_present()
        if self.has_resource:
            self.go_back_to_base()
            self.deliver_resource()
            if self.is_at_base():
                self.get_next_objective()
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
                 n_SBA, n_OBA, n_CA, height, width, n_resources , n_obstacles=0, base_pos = (0,0), seed=None):
        super().__init__(seed=seed)
        self.n_SA = n_SA
        self.n_SBA = n_SBA
        self.n_OBA = n_OBA
        self.schedule = []
        self.obstacles = []
        self.resources = {}
        self.grid = mesa.space.MultiGrid(height,width, torus=False)
        self.base_pos = base_pos

        for _ in range(n_resources):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            size = self.random.choice([Resource.SMALL, Resource.MEDIUM, Resource.HEAVY])
            r = Resource(size,self)
            self.grid.place_agent(r, (x,y))
            self.resources[(x,y)] = r

        for _ in range(n_obstacles):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            if (x,y) != base_pos:
                self.grid.place_agent(Obstacle(self), (x,y))
                self.obstacles.append((x,y))

        for _ in range(n_SA):
            a = SimpleAgent(self)
            self.schedule.append(a)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_SBA):
            a = StateBasedAgent(self)
            self.schedule.append(a)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_OBA):
            a = ObjectiveBasedAgent(self)
            self.schedule.append(a)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_CA):
            a = CooperativeAgent(self)
            self.schedule.append(a)
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
        for agent in self.schedule:
            agent.step()