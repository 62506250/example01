from abc import ABC, abstractmethod
import pygame


class GameEntity(ABC):

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._alive = True

    @property
    def position(self):
        return (self._x, self._y)

    @position.setter
    def position(self, value):
        self._x = value[0]
        self._y = value[1]

    @property
    def alive(self):
        return self._alive

    def kill(self):
        self._alive = False

    @abstractmethod
    def update(self, dt):
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface):
        raise NotImplementedError

    @abstractmethod
    def get_rect(self):
        raise NotImplementedError

    def collides_with_point(self, point):
        rect = self.get_rect()
        return rect.collidepoint(point)
