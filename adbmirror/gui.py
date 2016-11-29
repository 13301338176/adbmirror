import pygame
import cStringIO
import sys

from capclient import CapClient
from touchclient import TouchClient

class Main():
    def __init__(self):
        assert len(sys.argv) == 4
        self.size = map(int, sys.argv[1].split("x"))
        orig = map(int, sys.argv[2].split("x"))
        self.orig = orig[1], orig[0]
        self.path = sys.argv[3]
        
        
        self.scalel = True
        self.scalep = False
        
        ml = self.orig[0] / float(self.size[0])
        self.sizel = self.size[0], int(self.orig[1] / ml)
        self.yl = (self.size[1] - self.sizel[1]) / 2                

        mp = self.orig[0] / float(self.size[1])
        self.sizep = int(self.orig[1] / mp), self.size[1]
        self.xp = int((self.size[0] - self.sizep[0]) / 2)
        
        self.screen = pygame.display.set_mode(self.size)
        
        self.cap = CapClient(self)
        self.cap.start()
        
        self.touch = TouchClient(self)
        self.touch.start()
        
        self.mouse_down = False

        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.cap.write(["end"])
                self.touch.write(["end"])
               
               
            if hasattr(event, "pos"):
                ix, iy = event.pos
                if self.landscape:
                    y = (ix / float(self.size[0]))
                    if self.scalel:
                        x = 1.0 - (iy / float(self.size[1]))
                    else:
                        x = 1.0 - (((iy - self.yl)) / float(self.sizel[1]))

                else:
                    y = iy / float(self.size[1])
                    if self.scalep:
                        x = ix  / float(self.size[0])
                    else:
                        x = ((ix - self.xp)) / float(self.sizep[0])
                           
                x = min(max(0, x), 1)
                y = min(max(0, y), 1)
#                 print x, y
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.touch.write(["down", x, y])
                self.mouse_down = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.touch.write(["up"])
                self.mouse_down = False

            if event.type == pygame.MOUSEMOTION:
                if self.mouse_down:
                    self.touch.write(["move", x, y])
            
        
    def run(self):
        self.running = True
        self.landscape = None
        
        while self.running:
            self.events()
            
            for msg in self.cap.read():
                cmd = msg[0]
                if cmd == "head":
                    self.banner = msg[1]

                if cmd == "data":
                    data = cStringIO.StringIO(msg[1])
                    a = pygame.image.load(data)
                    landscape = sum(a.get_at((self.size[1] + 10, self.size[0] / 2))) > sum(a.get_at((self.size[0] / 2, self.size[1] + 10)))
                    if self.landscape is not landscape:
                        self.landscape = landscape
                        self.screen.fill((0, 0, 0))

                    if self.landscape:       
                        if self.scalel:
                            a = a.subsurface(pygame.Rect((0,0), self.sizel))
                            a = pygame.transform.smoothscale(a, self.size)
                            y = 0
                        else:
                            y = self.yl 
                        self.screen.blit(a, (0, y))
                    else:
                        a = pygame.transform.smoothscale(a, (self.size[1], self.size[1]))
                        if self.scalep:
                            a = a.subsurface(pygame.Rect((0,0), self.sizep))
                            a = pygame.transform.smoothscale(a, self.size)
                            x = 0
                        else:
                            x = self.xp
                        self.screen.blit(a, (x, 0))
                        
                    pygame.display.update()
             
a = Main()
a.run()
