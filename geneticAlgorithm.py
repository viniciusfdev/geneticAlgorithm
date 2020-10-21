import matplotlib.pyplot as plt
import numpy as np
import random
import math
import time

"""
# Vinícius França Lima Vilaça

# Exige a instalação das bibliotecas matplotlib e numpy para o plot
# pip install matplotlib
# pip install numpy

# Tamanho da população: Caso não seja inputada pelo usuário = 10  
# Forma de seleção: Seleção por ranking linear  
# Tipo de crossover: Crossover aritmético
# Função objetivo: 𝑓(𝑥, 𝑦) = sin(𝑥) 𝑒^(1−cos(𝑦))^2 + 𝑐𝑜𝑠(𝑦)𝑒^(1−sin (𝑥))^2 + (𝑥 − 𝑦)^2
# Função de Fitness: 𝑓(𝑥, 𝑦) = sin(𝑥) 𝑒^(1−cos(𝑦))^2 + 𝑐𝑜𝑠(𝑦)𝑒^(1−sin (𝑥))^2 + (𝑥 − 𝑦)^2
# Número Máximo de Gerações: Padrão: 1000 (ou até encontrar o melhor)
# Taxa de Crossover: 50%
# Taxa de Mutação: 5%
"""

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
        self.path = { "best": [], "average": [], "worst": []}

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
            alternada dos pais, a alternação ocorre com 70% de chance
        """
        if random.random() > 0.7:
            return pa, pb

        rand_mut = random.random()

        return (Individual(pb.x * (1-rand_mut) + pa.x * rand_mut, pb.y * (1-rand_mut) + pa.y * rand_mut),
                Individual(pa.x * (1-rand_mut) + pb.x * rand_mut, pa.y * (1-rand_mut) + pb.y * rand_mut))

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
        
    def select_with_rep(self):
        """
            seleção por ranking linear
        """
        MIN = 0
        MAX = 100
        sorted_c = self.sort_by_fitness()
        
        
        ps = [] # probabilidade de seleção
        for i, idv in enumerate(sorted_c):
            ps.append(MIN + (MAX - MIN) * (len(sorted_c)-i)/(len(sorted_c)-1))

        ss = [] # probabilidade de seleção acumulada
        for i, idv in enumerate(sorted_c):
            if i == 0:
                ss.append(ps[i])
            else:
                ss.append(ss[i-1] + ps[i])

        # selecao por ranking linear
        for i in range(round(len(sorted_c)/2)):
            rand_a = random.uniform(ss[0], ss[len(ss)-1])
            rand_b = random.uniform(ss[0], ss[len(ss)-1])
            pos_a = 0
            pos_b = 0
            
            # procura na roleta as duas posicoes dos pais sorteados
            # considerando os pesos(da selecao acumulada) ss calculado
            # anteriormente
            for pos in range(len(ss)):
                if pos == 0:
                    if rand_a < ss[pos]:
                        pos_a = pos
                        break

                if rand_a <= ss[pos-1] and rand_a < ss[pos]:
                    pos_a = pos
                    break

                if rand_b <= ss[pos-1] and rand_b < ss[pos]:
                    pos_b = pos
                    break

            yield sorted_c[pos_a], sorted_c[pos_b]

    def select_by_class(self):
        """
            Seleção por elitismo, a seleção randomica é feita sob
            30% dos melhores (nao é utilizada na pratica, foi feita a 
            titulo de curiosidade e testes)
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
        return self.sort_by_fitness()[0]

    @staticmethod
    def fitness(x, y) -> float:
        """
            Função fitness para avaliar o individuo
        """
        return (math.sin(x) * math.exp((1-math.cos(y))**2) + 
                math.cos(y) * math.exp((1-math.sin(x))**2) + 
                (x-y)**2)

    def get_average(self):
        """
            Recupera o fitness medio da população corrente
        """
        return sum([idv.fitness for idv in self.population]) / len(self.population)

    def get_worst(self):
        return self.sort_by_fitness()[len(self.population)-1]

    def save_all(self):
        """
            Salva todos os dados da população atual
        """
        self.path["best"].append(self.get_best().fitness)
        self.path["average"].append(self.get_average())
        self.path["worst"].append(self.get_worst().fitness)

    def run(self) -> int:
        """
            Executa um loop até encontrar o melhor x e y que se 
            aproxima do GLOBAL_MIN (minimo global)
        """

        # para comparar os valores se usa 
        i = 1
        while i < self.max_it:
            self.assess_fitness()
            self.save_all()
            if (self.get_best().fitness == self.GLOBAL_MIN):
                return i

            q_pop = []
            for pa, pb in self.select_with_rep():
                child_a, child_b = self.cross_over(pa, pb)
                q_pop.append(self.mutate(child_a))
                q_pop.append(self.mutate(child_b))

            self.population = q_pop

            i = i + 1

        self.assess_fitness()

        return i

if __name__ == "__main__":
    pop = Population(1000, 10)
    init_time = time.time()
    generations = pop.run()

    print("População final:\n {}".format(pop.population))
    print("Execution time: {}".format(time.time() - init_time))
    print("Number of generations: {}".format(generations))

    gen_dist = range(generations-1)
    best_line = np.linspace(0, generations)

    # second poly fit to plot the aproximation
    best_model = np.poly1d(np.polyfit(gen_dist, pop.path["best"], 3))
    worst_model = np.poly1d(np.polyfit(gen_dist, pop.path["worst"], 3))
    average_model = np.poly1d(np.polyfit(gen_dist, pop.path["average"], 3))
    
    plt.plot(best_line, best_model(best_line), 'g', label='Best')
    plt.plot(best_line, worst_model(best_line), 'r', label='Worst')
    plt.plot(best_line, average_model(best_line), 'b', label='Average')

    plt.legend(['Best', 'Worst', 'Average'])

    plt.xlabel('generations')
    plt.ylabel('fitness')
    plt.show()
