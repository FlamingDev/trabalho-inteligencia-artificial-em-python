import mesa

class Obstacle(mesa.Agent):

    def __init__(self, model):
        super().__init__(model)
        self.type = "Obstacle" 
        self.color = "gray"  
        self.shape = "diamond"  