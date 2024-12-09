import random
import pandas as pd
import mesa
#from mesa.time import RandomActivation
from numpy.matlib import empty

from SimpleAgent import SimpleAgent
from ObjectiveBasedAgent import ObjectiveBasedAgent
from StateBasedAgent import StateBasedAgent
from CooperativeAgent import CooperativeAgent
from Resource import Resource
from Obstacle import Obstacle


class Planet(mesa.Model):
    def __init__(self, n_SA,
                 n_SBA, n_OBA,n_CA, height, width, n_resources , n_obstacles=0, base_pos = (0,0), seed=None):
        super().__init__(seed=seed)
        self.random.seed(seed)  # Semente para consistência
        # self.n_SA = n_SA;
        # self.n_SBA = n_SBA
        # self.n_OBA = n_OBA
        # self.obstacles = []
        # self.grid = mesa.space.MultiGrid(int(width), int(height), torus=False)
        # self.base_pos = base_pos

        # for _ in range(n_resources):
        #     x, y = self.random.randrange(width), self.random.randrange(height)
        #     while (x, y) == base_pos or (x, y) in self.obstacles:
        #         x, y = self.random.randrange(width), self.random.randrange(height)
        #     size = self.random.choice([Resource.SMALL, Resource.MEDIUM, Resource.HEAVY])
        #     self.grid.place_agent(Resource(size, self), (x, y))

        # for _ in range(n_obstacles):
        #     x, y = self.random.randrange(width), self.random.randrange(height)
        #     while (x, y) == base_pos or (x, y) in self.obstacles:
        #         x, y = self.random.randrange(width), self.random.randrange(height)
        #     self.grid.place_agent(Obstacle(self), (x, y))
        #     self.obstacles.append((x, y))


        # for _ in range(n_SA):
        #     a = SimpleAgent(self)
        #     self.grid.place_agent(a, base_pos)

        # for _ in range(n_SBA):
        #     b = StateBasedAgent(self)
        #     self.grid.place_agent(b, base_pos)

        # for _ in range(n_OBA):
        #     c = ObjectiveBasedAgent(self)
        #     self.grid.place_agent(c, base_pos)

        # for _ in range(n_CA):
        #     a = CooperativeAgent(self)
        #     self.schedule.append(a)
        #     self.grid.place_agent(a, base_pos)

        self.n_SA = n_SA
        self.n_SBA = n_SBA
        self.n_OBA = n_OBA
        self.schedule = []
        self.obstacles = []
        self.resources = {}
        self.grid = mesa.space.MultiGrid(int(width), int(height), torus=False)
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


    def step(self):
    # Verifica todos os agentes
        for agent in self.agents:
            if isinstance(agent, SimpleAgent):
                agent.step()  

        for (x, y) in self.obstacles:
            if not any(isinstance(obj, Obstacle) for obj in self.grid.get_cell_list_contents((x, y))):
                self.grid.place_agent(Obstacle(self), (x, y))

    

    def to_dataframe(self):
        self.data = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                for obj in cell_contents:
                    if hasattr(obj, "color") and hasattr(obj, "shape"):
                        if isinstance(obj, Resource):
                            resource_type = f"Resource ({'SMALL' if obj.size == Resource.SMALL else 'MEDIUM' if obj.size == Resource.MEDIUM else 'HEAVY'})"
                        else:
                            resource_type = obj.__class__.__name__
                        self.data.append({
                            "x": int(x),
                            "y": int(y),
                            "type": resource_type,  
                            "color": obj.color,  
                            "shape": obj.shape
                        })
                    else:
                        print(f"Objeto na posição ({x}, {y}) não possui 'color' ou 'shape': {obj}")
        
        return pd.DataFrame(self.data)



