from StateBasedAgent import StateBasedAgent
from Resource import Resource

class ObjectiveBasedAgent(StateBasedAgent):
    def __init__(self, model):
        super().__init__(model)
        self.known_resources = list()
        self.next_objective = None
        self.type = "ObjectiveBasedAgent"  
        self.color = "black" 
        self.shape = "cross"

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
