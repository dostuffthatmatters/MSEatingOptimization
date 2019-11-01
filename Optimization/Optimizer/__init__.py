from abc import ABC, abstractmethod

class Optimizer(ABC):

    @staticmethod
    def optimize():
        """
        The goal here is to determine Host.guests/Guest.host for all Host aud Guest instances
        :return: None
        """
        raise NotImplementedError
