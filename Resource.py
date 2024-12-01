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
            
            self.color = "blue" 
        elif size == self.MEDIUM:
            self.utility = 20
            
            self.color = "orange" 
        else:
            self.utility = 50
            self.color = "red" 

    @property
    def color(self):
        return self._color

    @property
    def shape(self):
        return self._shape
    
    @shape.setter
    def shape(self, value):
        print(f"Alterando cor de {self.type} para {value}")
        self._shape = value
    
    @color.setter
    def color(self, value):
        print(f"Alterando cor de {self.type} para {value}")
        self._color = value