from typing import List
import pygame

font: pygame.font.Font = None
def setFont(_font: pygame.font.Font):
    global font
    font = _font

class Board:
    def __init__(self):
        self.components = []

    def stepBoard(self):
        for component in self.components:
            if isinstance(component, Interactable):
                component.update()

    def addComponents(self, *components):
        for component in components:
            self.components.append(component)
            component.update()

    def draw(self, screen: pygame.surface.Surface):
        for component in self.components:
            component.draw(screen)


class Component:
    def __init__(self, name=None):
        self.sockets = []
        self.position = [0, 0]
        self.size = [60, 50]
        if name:
            self.text = font.render(name, True, (255, 255, 255))

    def draw(self, screen):
        if hasattr(self, "text"):
            screen.blit(self.text, self.text.get_rect(center = (self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2)))
            pygame.draw.rect(screen, (200, 0, 200), pygame.Rect(*self.position, *self.size), 3)

            j, k = 0, 0
            for socket in self.sockets:
                if socket.type == SocketType.INPUT:
                    socket.position = (self.position[0], self.position[1] + (j+1) * 10)
                    pygame.draw.circle(screen, (0, 255, 0) if socket.state else (255, 0, 0), socket.position, 3)
                    j += 1
                elif socket.type == SocketType.OUTPUT:
                    socket.position = (self.position[0] + 60, self.position[1] + (k+1) * 10)
                    pygame.draw.circle(screen, (0, 255, 0) if socket.state else (255, 0, 0), socket.position, 3)
                    k += 1

    def update(self):
        pass

class Connection(Component):
    def __init__(self, *sockets):
        super().__init__()
        self.state = False
        self.sockets = sockets
        socket: Socket
        for socket in self.sockets:
            socket.setConnection(self)

    def update(self, state=None):
        if state != None and self.state != state:
            self.state = state
            socket: Socket
            for socket in self.sockets:
                socket.setState(state)

    def draw(self, screen):
        inputs = [socket for socket in self.sockets if socket.type == SocketType.INPUT]
        outputs = [socket for socket in self.sockets if socket.type == SocketType.OUTPUT]
        for x in inputs:
            for y in outputs:
                pygame.draw.aaline(screen, (0, 255, 0) if self.state else (255, 0, 0), x.position, y.position, 1)


class SocketType:
    INPUT = 0
    OUTPUT = 1

class Socket:
    def __init__(self, state=False):
        self.state = state
        self.component = None
        self.connection = None
        self.type = None
        self.position = []

    def setComponent(self, component: Component):
        self.component = component

    def setConnection(self, connection: Connection):
        self.connection = connection

    def setType(self, type: SocketType):
        self.type = type
        return self
    
    def setState(self, state):
        if self.state != state:
            self.state = state
            if self.type == SocketType.INPUT:
                self.component.update()
            if self.type == SocketType.OUTPUT:
                if self.connection:
                    self.connection.update(self.state)


class Interactable:
    def __init__(self):
        pass

class Button(Component, Interactable):
    def __init__(self):
        super().__init__("BUT")
        self.sockets = [Socket().setType(SocketType.OUTPUT)]
        for socket in self.sockets:
            socket.setComponent(self)

    def update(self):
        old = self.sockets[0].state
        new = pygame.mouse.get_pressed() and pygame.rect.Rect([*self.position, *self.size]).collidepoint(*pygame.mouse.get_pos())
        if new != old:
            self.sockets[0].setState(new)
            

class Switch(Component, Interactable):
    def __init__(self):
        super().__init__("SWC")
        self.sockets = [Socket().setType(SocketType.OUTPUT)]
        for socket in self.sockets:
            socket.setComponent(self)
        self.old = None

    def update(self):
        new = pygame.mouse.get_pressed()[0] and pygame.rect.Rect([*self.position, *self.size]).collidepoint(*pygame.mouse.get_pos())
        if self.old != new and new:
            self.sockets[0].setState(not self.sockets[0].state)
        self.old = new


class OR(Component):
    def __init__(self):
        super().__init__("OR")
        self.sockets: List[Socket]
        self.sockets = [Socket().setType(SocketType.INPUT), Socket().setType(SocketType.INPUT), Socket().setType(SocketType.OUTPUT)]
        for socket in self.sockets:
            socket.setComponent(self)

    def update(self):
        self.sockets[2].setState(self.sockets[0].state or self.sockets[1].state)

class NOR(Component):
    def __init__(self):
        super().__init__("NOR")
        self.sockets: List[Socket]
        self.sockets = [Socket().setType(SocketType.INPUT), Socket().setType(SocketType.INPUT), Socket().setType(SocketType.OUTPUT)]
        for socket in self.sockets:
            socket.setComponent(self)

    def update(self):
        self.sockets[2].setState(not (self.sockets[0].state or self.sockets[1].state))

class NAND(Component):
    def __init__(self):
        super().__init__("NAND")
        self.sockets: List[Socket]
        self.sockets = [Socket().setType(SocketType.INPUT), Socket().setType(SocketType.INPUT), Socket().setType(SocketType.OUTPUT)]
        for socket in self.sockets:
            socket.setComponent(self)

    def update(self):
        self.sockets[2].setState(not (self.sockets[0].state and self.sockets[1].state))

def evalState(node):
    while callable(node):
        node = node()
    return node

def main():
    pygame.init()
    screen_size = (1920/2, 1080/2)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Logic Sim Test")
    pygame.display.set_icon(pygame.image.load(r"resources\not.png"))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    setFont(font)

    board = Board()

    switch1 = Switch()
    switch1.position = [100, 100]
    switch2 = Switch()
    switch2.position = [100, 200]

    nor1 = NAND()
    nor1.position = [170, 100]
    nor2 = NAND()
    nor2.position = [170, 200]

    conn1 = Connection(switch1.sockets[0], nor1.sockets[0])
    conn2 = Connection(switch2.sockets[0], nor2.sockets[0])

    conn3 = Connection(nor1.sockets[2], nor2.sockets[1])
    conn4 = Connection(nor2.sockets[2], nor1.sockets[1])

    board.addComponents(switch1, switch2, nor1, nor2, conn1, conn2, conn3, conn4)

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        board.stepBoard()

        board.draw(screen)
        # board.displayText()

        pygame.display.flip()
        clock.tick(128)
    
    pygame.quit()

if __name__ == "__main__":
    main()  