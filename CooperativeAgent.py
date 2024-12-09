from ObjectiveBasedAgent import ObjectiveBasedAgent
from Resource import Resource

# class CooperativeAgent(ObjectiveBasedAgent):
#     def __init__(self, model):
#         super().__init__(model)
#         self.blocked = False
#         self.help_requests = set()

#     def calculate_distance(pos1, pos2):
#         return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

#     def collect_resource_if_present(self):
#         cell_contents = self.model.grid.get_cell_list_contents(self.pos)
#         for obj in cell_contents:
#             if isinstance(obj, Resource):
#                 if not self.has_resource and obj.size != obj.HEAVY:
#                     self.has_resource = True
#                     self.current_resource = obj
#                     self.model.grid.remove_agent(obj)
#                 elif self.pos not in self.known_resources and obj.size != obj.HEAVY:
#                     self.known_resources.append(self.pos)

#                 else:
#                     other_agent = next(
#                         (agent for agent in cell_contents if isinstance(agent, CooperativeAgent) and agent != self), None)
#                     if other_agent:
#                         self.has_resource = True
#                         self.current_resource = obj
#                         other_agent.has_resource = True
#                         self.model.grid.remove_agent(obj)
#                         print(f"{self.unique_id} e {other_agent.unique_id} estão compartilhando o recurso!")


#     def ask_for_help(self, target_resource):
#         for agent in self.model.agents:
#             if isinstance(agent, CooperativeAgent) and agent != self:
#                 agent.help_requests.add(target_resource)

#     def respond_to_request(self):
#         for request in self.help_requests:
#             resource_pos = request
#             if self.calculate_distance(self.pos, resource_pos) <= 2:
#                 self.help_requests.remove(request)
#                 print(f"Agent {self.unique_id} decided to help the agent at {resource_pos}!")
#                 return resource_pos
#             else:
#                 print(f"Agent {self.unique_id} declined the help request at {resource_pos}.")
#         return None

#     def step(self):
#         self.collect_resource_if_present()
#         if self.has_resource:
#             self.go_back_to_base()
#             self.deliver_resource()
#             if self.is_at_base():
#                 self.get_next_objective()
#         else:
#             if self.next_objective is not None:
#                 print(f"{self.unique_id } TEM UM OBJETIVO AGORA")
#                 self.go_to_next_objective()
#             else:
#                 self.move()

class CooperativeAgent(ObjectiveBasedAgent):
    def __init__(self, model):
        super().__init__(model)
        self.blocked = False
        self.partner = None  # Referência ao agente parceiro (se estiver cooperando)
        self.help_requests = []  # Solicitações de ajuda pendentes
        self.type = "Cooperative Agente"
        self.color = "black" 
        self.shape = "diamond"

    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def collect_resource_if_present(self):
        """Coleta recurso ou solicita ajuda para recurso pesado."""
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if isinstance(obj, Resource):
                if not self.has_resource and obj.size != obj.HEAVY:
                    self.has_resource = True
                    self.current_resource = obj
                    self.model.grid.remove_agent(obj)
                elif self.pos not in self.known_resources and obj.size != obj.HEAVY:
                    self.known_resources.append(self.pos)
                elif obj.size == obj.HEAVY:
                    # Recurso pesado encontrado, solicita ajuda
                    if not self.partner:
                        self.ask_for_help(obj)
                    else:
                        self.cooperate_with_partner(obj)

    def ask_for_help(self, target_resource):
        """Solicita ajuda para carregar um recurso pesado."""
        for agent in self.model.schedule:
            if isinstance(agent, CooperativeAgent) and agent != self:
                distance = self.calculate_distance(self.pos, agent.pos)
                if distance <= 2 and not agent.has_resource and not agent.partner:
                    agent.partner = self
                    self.partner = agent
                    print(f"Agente {self.unique_id} solicitou ajuda de {agent.unique_id}.")
                    return

    
    def cooperate_with_partner(self, resource):
        """Ambos os agentes carregam o recurso até a base."""
        self.has_resource = True
        self.current_resource = resource
        self.partner.has_resource = True
        self.partner.current_resource = resource
        self.model.grid.remove_agent(resource)
        print(f"Agentes {self.unique_id} e {self.partner.unique_id} estão carregando o recurso {resource.type}!")

    def deliver_resource(self):
        """Entrega o recurso e libera o parceiro se aplicável."""
        if self.has_resource and self.is_at_base():
            if self.current_resource is not None:
                self.collected_resources += 1
                self.score += self.current_resource.utility
            self.current_resource = None
            self.has_resource = False
            if self.partner:
                self.partner.current_resource = None
                self.partner.has_resource = False
                self.partner = None
                print(f"Agente {self.unique_id} e seu parceiro completaram a entrega.")

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