from abc import ABC, abstractmethod

class Optimizer(ABC):

    @staticmethod
    def optimize():
        raise NotImplementedError
