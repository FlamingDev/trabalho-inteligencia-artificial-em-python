import mesa

class Resource(mesa.Agent):
    SMALL = 0
    MEDIUM = 1
    HEAVY = 2

    def __init__(self, size, model):
        super().__init__(model)
        self.size = size
        self.type = f"Resource (Size {size})"
        self.shape = "circle"

        if size == self.SMALL:
            self.utility = 10
            
            self.color = "green" 
        elif size == self.MEDIUM:
            self.utility = 20
            
            self.color = "orange" 
        else:
            self.utility = 50
            
            self.color = "red" 