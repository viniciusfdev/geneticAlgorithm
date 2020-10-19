import random
import math

class Individual:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fitness = None

    def __repr__(self):
        return "x: {}, y: {}, z: {}\n".format(self.x, self.y, self.fitness)

class Population:
    MIN = -10
    MAX = 10
    GLOBAL_MIN = -106.764537
    def __init__(self, max_it, pop_size):
        self.max_it = max_it
        self.pop_size = pop_size
        self.population = self.create_rand_pop()

    def create_rand_pop(self):
        pop = []
        for i in range(self.pop_size):
            pop.append(Individual(
                random.uniform(self.MIN, self.MAX),
                random.uniform(self.MIN, self.MAX)
                ))

        return pop

    def assess_fitness(self):
        """
            add fitness attribute to all of the items
        """
        for i, idv in enumerate(self.population):
            self.population[i].fitness = self.fitness(idv.x, idv.y)
    
    def cross_over(self, pa, pb) -> (Individual, Individual):
        """
            a função cross over para cada filho retorna uma coordenada
            alternada dos pais, a alternação ocorre dentre todos as 
            permutações de pa e pb P(n,r) = 12 logo, 1/12
        """
        px = [pa.x, pb.x]
        py = [pa.y, pb.y]

        return (Individual(random.choice(px), random.choice(py)),
                Individual(random.choice(px), random.choice(py)))

    def mutate(self, idv) -> (Individual, Individual):
        """
            Implementa uma BUSCA LOCAL através de ajustes aleatórios em
            ambas as direções caso o gene aleatoriamente seja mutado
            5% de chance de mutação por gene
        """
        mute_x = True if round(random.uniform(1, 20)) == 1 else False
        mute_y = True if round(random.uniform(1, 20)) == 1 else False
        
        return Individual(
            idv.x + random.uniform(-1, 1) if mute_x else idv.x,
            idv.y + random.uniform(-1, 1) if mute_y else idv.y,)
        
    def select_by_class(self):
        """
            Seleção por classificação, a seleção randomica é feita sob
            30% dos melhores
        """
        sorted_c = self.sort_by_fitness()[:round(0.30*len(self.population))]
    
        for i in range(round(0.5*len(self.population))):
            yield random.choice(sorted_c), random.choice(sorted_c)
    
    def sort_by_fitness(self) -> list:
        """
            Ordenação pela melhor adequação
        """
        return sorted(
            self.population,  
            key=lambda idv: idv.fitness)

    def get_best(self) -> Individual:
        """
            Retorna o melhor individuo da população
        """
        best = self.population[0]
        for idv in self.population:
            if idv.fitness < best.fitness:
                best = idv
        
        return best

    @staticmethod
    def fitness(x, y) -> float:
        """
            Função fitness para avaliar o individuo
        """
        return (math.sin(x) * math.exp((1-math.cos(y))**2) + 
                math.cos(y) * math.exp((1-math.sin(x))**2) + 
                (x-y)**2)

    def run(self) -> int:
        """
            Executa um loop até encontrar o melhor x e y que se 
            aproxima do GLOBAL_MIN (minimo global)
        """

        # para comparar os valores se usa 
        i = 1
        while i < self.max_it:
            self.assess_fitness()
            if (round(self.get_best().fitness) == round(self.GLOBAL_MIN)):
                return i
            
            q_pop = []
            for pa, pb in self.select_by_class():
                child_a, child_b = self.cross_over(pa, pb)
                q_pop.append(self.mutate(child_a))
                q_pop.append(self.mutate(child_b))

            self.population = q_pop

            i = i + 1

        self.assess_fitness()

        return i

if __name__ == "__main__":
    pop = Population(1000, 100)

    #pop.assess_fitness()

    #print(pop.population)

    n = pop.run()
    print(pop.population)
    print("Number of iterations: {}".format(n))