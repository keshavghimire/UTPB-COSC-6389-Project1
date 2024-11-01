import math
import random
import tkinter as tk
from tkinter import *

num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

screen_padding = 25
item_padding = 5
stroke_width = 5

num_generations = 1000
pop_size = 50
elitism_count = 2
mutation_rate = 0.05

sleep_time = 100

# Helper function to generate a random RGB color
def random_rgb_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
    return hex_color

# Class to represent an item with value and color
class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)
        self.color = random_rgb_color()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def place(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, active=False):
        gap = 14
        if active:
            canvas.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h, fill=self.color, outline=self.color, width=stroke_width)
        else:
            canvas.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h, fill='', outline=self.color, width=stroke_width)
        canvas.create_text(self.x + self.w + gap, self.y + self.h / 2, text=f'{self.value}', anchor='w', font=('Arial', 12), fill='white')

# Genetic Algorithm Class
class GeneticAlgorithm:
    def __init__(self, items_list, target, pop_size, num_generations, mutation_rate, elitism_count):
        self.items_list = items_list
        self.target = target
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.population = []
        self.generation = 0
        self.best_genome = None
        self.running = False

    def gene_sum(self, genome):
        return sum(item.value for idx, item in enumerate(self.items_list) if genome[idx])

    def fitness(self, genome):
        total_value = self.gene_sum(genome)
        return 1 / (1 + abs(self.target - total_value))

    def generate_initial_population(self):
        self.population = [[random.random() < frac_target for _ in range(len(self.items_list))] for _ in range(self.pop_size)]

    def select_parents(self, population, fitnesses, tournament_size=3):
        def tournament():
            competitors = random.sample(list(zip(population, fitnesses)), tournament_size)
            best = max(competitors, key=lambda x: x[1])[0]
            return best
        return tournament(), tournament()

    def crossover(self, parent1, parent2):
        return [parent1[i] if random.random() < 0.5 else parent2[i] for i in range(len(parent1))]

    def mutate(self, genome):
        for i in range(len(genome)):
            if random.random() < self.mutation_rate:
                genome[i] = not genome[i]
        return genome

    def evolve_population(self):
        fitnesses = [self.fitness(genome) for genome in self.population]
        sorted_population = sorted(zip(self.population, fitnesses), key=lambda x: x[1], reverse=True)
        new_population = [genome for genome, _ in sorted_population[:self.elitism_count]]

        while len(new_population) < self.pop_size:
            parent1, parent2 = self.select_parents([p for p, _ in sorted_population], [f for _, f in sorted_population])
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)

        self.population = new_population
        self.best_genome = sorted_population[0][0]

    def run_step(self):
        if self.generation == 0:
            self.generate_initial_population()

        self.evolve_population()
        self.generation += 1

        return self.best_genome, self.generation

# The main UI class
class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Knapsack")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        self.items_list = []

        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label='Knapsack', underline=0)

        menu_K.add_command(label="Generate", command=self.generate_knapsack, underline=0)
        menu_K.add_command(label="Get Target", command=self.set_target, underline=0)
        menu_K.add_command(label="Run", command=self.start_ga, underline=0)

        self.target = 0
        self.ga = None

    def get_rand_item(self):
        i1 = Item()
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None
        return i1

    def add_item(self):
        item = self.get_rand_item()
        while item is None:
            item = self.get_rand_item()
        self.items_list.append(item)

    def generate_knapsack(self):
        self.items_list.clear()
        for i in range(num_items):
            self.add_item()

        item_max = 0
        item_min = 9999
        for item in self.items_list:
            item_min = min(item_min, item.value)
            item_max = max(item_max, item.value)

        w = self.width - screen_padding
        h = self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(screen_padding + x * row_w + x * item_padding,
                           screen_padding + y * row_h + y * item_padding,
                           item_w,
                           item_h)

        self.clear_canvas()
        self.draw_items()

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        x = (self.width - screen_padding) / 8 * 7
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='yellow')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'Target: {int(self.target)}', font=('Arial', 18, 'bold'),fill='green')

    def draw_sum(self, item_sum, target):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        if target != 0:
            h *= (item_sum / target)
        else:
            h = 0
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='orange')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'Sum: {int(item_sum)}', font=('Arial', 18, 'bold'),fill='yellow')

    def draw_genome(self, genome, gen_num):
        for idx, item in enumerate(self.items_list):
            item.draw(self.canvas, active=genome[idx])
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 4 * 3
        self.canvas.create_text(x + w, y + h + screen_padding * 2, text=f'Generation {gen_num}', font=('Arial', 18,'bold'),fill='red')

    def get_item_sum(self, genome):
        return sum(item.value for idx, item in enumerate(self.items_list) if genome[idx])

    def set_target(self):
        item_sum = sum(item.value for item in self.items_list)
        self.target = item_sum * frac_target
        self.clear_canvas()
        self.draw_items()
        self.draw_target()

    def start_ga(self):
        self.ga = GeneticAlgorithm(self.items_list, self.target, pop_size, num_generations, mutation_rate, elitism_count)
        self.run_ga()

    def run_ga(self):
        if self.ga:
            # Run a generation step
            genome, gen_num = self.ga.run_step()

            # Calculate the sum and fitness of the current best genome
            item_sum = self.get_item_sum(genome)
            fitness = self.ga.fitness(genome)

            # Print the generation details
            print(f"Generation {gen_num}, Sum: {item_sum}, Fitness: {fitness:.2f}")

            # Clear and update the canvas visuals
            self.clear_canvas()
            self.draw_items()
            self.draw_target()
            self.draw_sum(item_sum, self.target)
            self.draw_genome(genome, gen_num)

            # Check if the exact solution is found
            if item_sum == self.target:
                print("Exact solution found!")
            elif self.ga.generation < num_generations:
                # Continue to the next generation after a delay
                self.after(sleep_time, self.run_ga)


app = UI()
app.mainloop()
