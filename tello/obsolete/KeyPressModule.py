import pygame


def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))


def getkey(keyname):
    ans = False
    for eve in pygame.event.get():
        pass
    keyinput = pygame.key.get_pressed()
    mykey = getattr(pygame, 'K_{}'.format(keyname))


    if keyinput[mykey]:
        ans = True
    pygame.display.update()
    return ans


def main():
    if getkey("LEFT"):
        return
    # print("Left key pressed")

    if getkey("RIGHT"):
        return
    # print("Right key Pressed")


if __name__ is True:
    init()
    while True:
        main()
