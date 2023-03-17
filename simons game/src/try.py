import socket
import errno
import time
import pickle

GAME_PORT = 6005
# participating clients must use this port for game communication


############## GAME LOGIC ##############

# sequence_og = []
# sequence_new = []


# def print_current_board():
    # print('sequence_og:', sequence_og)
    # print('sequence_new:', sequence_new)

def get_users_move(n):
    
    # n=n+1
    a=[]
    # a = list(map(int,input("\nEnter the numbers : ").strip().split()))[:n]
    while (len(a)!=n):
        a = list(map(int,input("\nEnter the numbers : ").strip().split()))[:n]
    return a

# def update_game_state(sequence_og,move):
    # global sequence_og, sequence_new
    # update the sequence arrays
    # sequence_og=move
    # if not sequence_og:
    #     sequence_og.append(int(move))
    # sequence_new.append(int(move))
    # pl=move[-1]
    # print(f'user played  {pl}')

def has_game_ended(sequence_og,move,n):
    # global n
    if(n==1):
        return False
    else:
      if move[:-1] == sequence_og:
          return False
      else:
          return True


############## EXPORTED FUNCTIONS ##############

def game_server(after_connect):
    # global sequence_og, sequence_new
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as accepter_socket:
        accepter_socket.bind(('', GAME_PORT))
        accepter_socket.listen(1)

        # non-blocking to allow keyboard interupts (^c)
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
                print("waiting for opp's move")
                received_data = (game_socket.recv(1024))
                
                if len(received_data) == 0:
                  break
                n+=1
                opp_move=pickle.loads(received_data)
                sequence_og=opp_move
                print(f'Opponent has played {opp_move[-1]}')
                # update_game_state('opp', opp_move)
                
                # if has_game_ended(opp_move):
                #     break
                # print("x2")
                # print_current_board()
                n+=1
                move = get_users_move(n)
                # print("x3")
                if has_game_ended(sequence_og,move,n):
                    print("you lost")
                    win_flag=0
                    break
                else:
                #   update_game_state(sequence_og,move)
                  sequence_og=move
                # print("x4")
                
                game_socket.send(pickle.dumps(move))
                
                
                

        # print_current_board()
        if(win_flag):
            print("you won")
        print('Game ended')

def game_client(opponent):
    # global sequence_og, sequence_new
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as game_socket:
        game_socket.connect((opponent, GAME_PORT))
        print('Game Started')
        sequence_og = []
        win_flag=1
        # sequence_new = []
        n=0

        while True:
            # print_current_board()
            n+=1
            move = get_users_move(n)
            if has_game_ended(sequence_og,move,n):
                print("you lost")
                win_flag=0
                break
            else:
              sequence_og=move #update fn
            # move = 
            game_socket.send(pickle.dumps(move))
            

            print("waiting for opp's move")
            received_data = game_socket.recv(1024)

            
            if len(received_data) == 0:
                break
            n+=1
            opp_move = pickle.loads(received_data)
            sequence_og=opp_move
            # print(opp_move)
            print(f'Opponent has played {opp_move[-1]}')
            
            # print_current_board()
            # if not opp_move:
            #     break
            
            # update_game_state('opp', opp_move)
            
            # if has_game_ended(opp_move):
            #     break
            
            
    if(win_flag):
        print("you won")
    print('Game ended')
