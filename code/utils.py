from random import random
from math import log


def uniform(a, b):
    return (b-a) * random() + a


def bernoulli(p):
    return 1 if random() < p else 0


def exponential(lmbda):
    return -log(random()) / lmbda
