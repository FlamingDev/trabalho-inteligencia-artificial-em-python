import mesa
from Resource import Resource

class SimpleAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.collected_resources = 0
        self.score = 0
        self.has_resource = False
        self.type = "Simple Agent"
        self.color = "blue" 
        self.shape = "square"

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)

        
        new_position = self.random.choice(possible_steps)

        cell_contents = self.model.grid.get_cell_list_contents(new_position)
        for obj in cell_contents:
            if isinstance(obj, Resource):
                # O agente pode interagir com o recurso, mas não deve alterar suas propriedades
                pass
    
        # Move o agente para a nova posição
        self.model.grid.move_agent(self, new_position)

    def collect_resource_if_present(self):
        
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        if cell_contents:  # Verificar se a célula não está vazia
            for obj in cell_contents:
                if isinstance(obj, Resource):
                    if obj.size != obj.HEAVY:
                        self.has_resource = True
                        self.model.grid.remove_agent(obj)
                        print(f"Removendo recurso: {obj.type}, Cor: {obj.color}, Forma: {obj.shape}")
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
                (self.move())

    def is_at_base(self):
        return self.pos == self.model.base_pos;

    def deliver_resource(self):
        if self.has_resource and self.is_at_base():
            self.collected_resources += 1
            self.has_resource = False

    def step(self):
        print(f"Agente {self.unique_id} na posição {self.pos}, tem recurso? {self.has_resource}")
        self.collect_resource_if_present()
        if self.has_resource:
            self.go_back_to_base()
            self.deliver_resource()
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