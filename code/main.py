from sys import argv
from queue import Queue
from utils import uniform, bernoulli, exponential


class KojoKitchen:
    def __init__(self, lmbda, total_time, total_employees, third_employee):
        self.lmbda = lmbda
        self.total_time = total_time
        self.third_employee = third_employee
        self.total_employees = total_employees

        self.next_arrival_time = self.arrival_time(lmbda)
        self.next_departure_time = [total_time +
                                    self.next_arrival_time] * total_employees
        self.is_employee_busy = [False] * self.total_employees
        self.queue = Queue()
        self.time = 0

        self.clients_to_attend = 0
        self.clients_served = 0
        self.clients_unhappy = 0

    def arrival_time(self, lmbda):
        return exponential(lmbda)

    def sandwich_time(self):
        return uniform(3, 5)

    def sushi_time(self):
        return uniform(5, 8)

    def food_type(self):
        return bernoulli(0.5)

    def get_order_time(self):
        return self.sushi_time() if self.food_type() else self.sandwich_time()

    def current_employees(self, time):
        if self.third_employee:
            # 11:30am - 1:30pm
            if 90 <= time and time <= 210:
                return 3

            # 5:00pm - 7:00pm
            if 420 <= time and time <= 540:
                return 3

        return 2

    def next(self):
        event = min(self.next_arrival_time, *self.next_departure_time)
        self.time = event
        employees = self.current_employees(self.time)

        if event == self.next_arrival_time:
            if event <= self.total_time:
                self.clients_to_attend += 1
                self.next_arrival_time = self.time + \
                    self.arrival_time(self.lmbda)
                for i in range(employees):
                    if not self.is_employee_busy[i]:
                        self.next_departure_time[i] = self.time + \
                            self.get_order_time()
                        self.is_employee_busy[i] = True
                        return True
                self.queue.put_nowait(event)
                return True
            else:
                # para que no hayan mas llegadas de clientes.
                self.next_arrival_time = max(*self.next_departure_time) + 1
                return any(self.is_employee_busy)

        for i in range(self.total_employees):
            # termina un cliente atendido por el empleado i.
            if event == self.next_departure_time[i]:
                self.clients_to_attend -= 1
                self.clients_served += 1
                if not self.queue.empty() and i < employees:
                    arrival = self.queue.get_nowait()
                    delay = event - arrival
                    self.clients_unhappy += 1 if delay > 5 else 0
                    self.next_departure_time[i] = self.time + \
                        self.get_order_time()
                else:
                    self.is_employee_busy[i] = False
                    self.next_departure_time[i] = self.total_time + \
                        self.next_arrival_time
                return True

        return False


if len(argv) != 2:
    print("Debe especificar el lambda")
    exit()

lmbda = float(argv[1])

print(f'Simulación para lambda={lmbda}')

total_clients = 0
total_unhappy_clients = 0
for _ in range(1000):
    kitchen = KojoKitchen(lmbda, 660, 2, False)
    while kitchen.next():
        pass
    total_clients += kitchen.clients_served
    total_unhappy_clients += kitchen.clients_unhappy

total_clients_mean = total_clients // 1000
total_unhappy_mean = total_unhappy_clients // 1000

print(
    f'Simulación con dos trabajadores -> Se atendieron como promedio {total_clients_mean} clientes de los cuales {total_unhappy_mean} resultaron insatisfechos, lo cual representa el {total_unhappy_mean *100 / total_clients_mean}% ')

total_clients = 0
total_unhappy_clients = 0
for _ in range(1000):
    kitchen = KojoKitchen(lmbda, 660, 3, True)
    while kitchen.next():
        pass
    total_clients += kitchen.clients_served
    total_unhappy_clients += kitchen.clients_unhappy

total_clients_mean = total_clients // 1000
total_unhappy_mean = total_unhappy_clients // 1000

print(
    f'Simulación con dos trabajadores -> Se atendieron como promedio {total_clients_mean} clientes de los cuales {total_unhappy_mean} resultaron insatisfechos, lo cual representa el {total_unhappy_mean *100 / total_clients_mean}% ')
