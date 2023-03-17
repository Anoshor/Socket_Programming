import socket
import errno
import time
import pickle
import pygame
import threading


pygame.font.init()


GAME_PORT = 6005
# participating clients must use this port for game communication


############## GAME LOGIC ##############

def get_seq(arr):
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    screen.fill((0,0,0))

    pygame.display.set_caption('Sequence generator')


    buttonRed = pygame.Rect(250,190,100,60)
    buttonBlue = pygame.Rect(350,250,60,100)
    buttonGreen = pygame.Rect(250,350,100,60)
    buttonYellow = pygame.Rect(190,250,60,100)

    


    def drawXX(button):
        pygame.draw.rect(screen,(255,255,255),button)
        pygame.display.update()
        if button == buttonRed:
            arr.append(1)
        if button == buttonBlue:
            arr.append(2)
        if button == buttonGreen:
            arr.append(3)
        if button == buttonYellow:
            arr.append(4)
        time.sleep(0.1)
    

    running = True
    while running:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False
            if events.type == pygame.KEYDOWN:
                if events.key==pygame.K_LCTRL:
                    running = False
            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_UP:
                    drawXX(buttonRed)
                if events.key == pygame.K_RIGHT:
                    drawXX(buttonBlue)
                if events.key == pygame.K_DOWN:
                    drawXX(buttonGreen)
                if events.key == pygame.K_LEFT:
                    drawXX(buttonYellow)
        
        pygame.draw.rect(screen,(255,0,0),buttonRed)    
        pygame.draw.rect(screen,(0,0,255),buttonBlue)    
        pygame.draw.rect(screen,(0,255,0),buttonGreen)    
        pygame.draw.rect(screen,(255,255,0),buttonYellow)    

        pygame.display.update()
    
    pygame.quit()


def get_users_move(n):
    
    
    a=[]
    
    while (len(a)!=n):
        # a = list(map(int,input("\nEnter the numbers : ").strip().split()))[:n]
        thread = threading.Thread(target=get_seq, args=(a,))
        thread.start()
        thread.join()
    print(a)
    return a



def has_game_ended(sequence_og,move,n):
    # global n
    if(n==1):
        return False
    else:
      if move[:-1] == sequence_og:
          return False
      else:
          return True



def run_game(screen, numbers):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    screen.fill((0,0,0))

    font=pygame.font.SysFont('comicsans',20)
    render=font.render("Press ctrl to display the sequence",1,(255,255,255))
    screen.blit(render,(200-(render.get_width())/2,200-(render.get_height())/2))
    pygame.display.update()


    if len(numbers) == 0:
        pygame.quit()
        return

    palette = {
        1: (255, 0, 0),
        2: (0, 0, 255),
        3: (0, 255, 0),
        4: (255, 255, 0)
    }

    def flash_palette(screen, color, duration):
        screen.fill(color)
        pygame.display.update()
        pygame.time.delay(duration)
        # screen.fill((0, 0, 0))
        # pygame.display.update()

    def flash_colors(screen, numbers):
        for num in numbers:
            color = palette[num]
            flash_palette(screen, color, 2000)
            # pygame.time.delay(2000)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_LCTRL:
                    running = False

            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     running = False
        
    flash_colors(screen,numbers)

        # screen.fill((111,76,111))
        # pygame.display.update()
    
    pygame.quit()






def game_server(after_connect):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as accepter_socket:
        accepter_socket.bind(('', GAME_PORT))
        accepter_socket.listen(1)

        
        accepter_socket.setblocking(False)
        while True:
            try:
                game_socket, addr = accepter_socket.accept()
            except socket.error as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    time.sleep(0.1)
                    continue
            break

        game_socket.setblocking(True)
        with game_socket:
            after_connect()
            print('Game Started')
            sequence_og = []
            win_flag=1
            # sequence_new = []
            n=0

            while True:
                
                

                # print("waiting for opp's move")
                received_data = (game_socket.recv(1024))
                
                if len(received_data) == 0:
                  break
                n+=1
                opp_move=pickle.loads(received_data)
                sequence_og=opp_move

                # pygame.init()
                # screen = pygame.display.set_mode((400, 400))
                
                thread = threading.Thread(target=run_game, args=(None, sequence_og))
                thread.start()
                thread.join()

                # print(f'Opponent has played {opp_move[-1]}')
                
                n+=1
                move = get_users_move(n)
                
                if has_game_ended(sequence_og,move,n):
                    print("you lost")
                    win_flag=0
                    break
                else:
                  sequence_og=move
                
                
                game_socket.send(pickle.dumps(move))
                
                
                

        
        if(win_flag):
            print("you won")
        print('Game ended')

def game_client(opponent):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as game_socket:
        game_socket.connect((opponent, GAME_PORT))
        print('Game Started')
        sequence_og = []
        win_flag=1
        
        n=0

        while True:
            
            

            n+=1
            move = get_users_move(n)
            if has_game_ended(sequence_og,move,n):
                print("you lost")
                win_flag=0
                break
            else:
              sequence_og=move #update fn
            
            game_socket.send(pickle.dumps(move))
            

            # print("waiting for opp's move")
            received_data = game_socket.recv(1024)

            
            if len(received_data) == 0:
                break
            n+=1
            opp_move = pickle.loads(received_data)
            sequence_og=opp_move

            # pygame.init()
            # screen = pygame.display.set_mode((400, 400))
            
            thread = threading.Thread(target=run_game, args=(None, sequence_og))
            thread.start()
            thread.join()
            
            # print(f'Opponent has played {opp_move[-1]}')
            
            
    if(win_flag):
        print("you won")
    print('Game ended')
