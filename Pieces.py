# This is where all of the piece functions will go.

import pygame
import GameBoard
import Player
import copy


class Piece:
    def __init__(self, name, starting_position, image, player):
        self.name = name
        self.starting_position = starting_position
        self.image = image
        self.player = player
        self.current_position = starting_position
        self.potential_moves = []
        if name == "Rook":
            if starting_position[1] == 0:
                self.sub_name = "KS"
            else:
                self.sub_name = "QS"
        if name == "King":
            self.castle_QS = True
            self.castle_KS = True

    def display_piece_to_screen(self, tiles, gameDisplay):
        # Takes in an array of tiles
        for tile in tiles:
            if(tile.coordinate == self.current_position):
                #display the image to the screen

                #Need to change self.image to be a surface rather than a string
                image_to_draw = pygame.image.load(self.image)
                image_rect = image_to_draw.get_rect()
                image_rect.center = (tile.x_position + tile.height/2, tile.y_position + tile.height/2)
                gameDisplay.blit(image_to_draw, image_rect)

    def get_piece_on_tile(self,coordinate, player_1_pieces, player_2_pieces):
        for piece in player_1_pieces:
            if piece.current_position == coordinate:
                return piece
        for piece in player_2_pieces:
            if piece.current_position == coordinate:
                return piece
        return None

    def crop_potential_moves(self, tiles, player_1_pieces, player_2_pieces):
        final_moves = []
        for move in self.potential_moves:
            if(move[0] >= 0 and move[0] < 8 and move[1] >= 0 and move[1] < 8):
                final_moves.append(move)
        #Create two deep copies for each of the player pieces
        #copy_1 = copy.deepcopy(player_1_pieces)
        #copy_2 = copy.deepcopy(player_2_pieces)
        self.potential_moves = final_moves
        return final_moves

    def induces_check(self, tiles, player_1_pieces, player_2_pieces):
        #Change this so we are working with copies
        copy_1 = copy.deepcopy(player_1_pieces)
        copy_2 = copy.deepcopy(player_2_pieces)
        for piece in copy_1:
            if piece.current_position == self.current_position:
                copy_self = piece
        for piece in copy_2:
            if piece.current_position == self.current_position:
                copy_self = piece
        # induces check calls itself in a recursive loop
        # Could be a potential bug in this loop:
        final_moves = copy_self.potential_moves
        delete_list = []
        for i in range(len(copy_self.potential_moves)):
            #print(str(self.potential_moves[i][0])+", "+str(self.potential_moves[i][1]))
            copy_self.move_piece(tiles[copy_self.potential_moves[i][0]*8+copy_self.potential_moves[i][1]],
                       tiles, copy_1, copy_2)
            if copy_self.player == 1:
                if(copy_self.check(tiles, copy_1, copy_2, 2)):
                    delete_list.append(i)
            if copy_self.player == 2:
                if(self.check(tiles, copy_1, copy_2, 1)):
                    delete_list.append(i)
        counter = 0
        for i in range(len(delete_list)):
            del final_moves[delete_list[i]-counter]
            counter = counter + 1
        self.potential_moves = final_moves
        return self.potential_moves

    def empty_square(self, tile, player_1_pieces, player_2_pieces, i, max_i):
        name = self.name
        if name == "Queen" or name == "Bishop" or name == "Rook":
            for piece in player_1_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    return max_i
                if piece.current_position == tile and piece.player != self.player:
                    return max_i-1
                    
            for piece in player_2_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    return max_i
                if piece.current_position == tile and piece.player != self.player:
                    return max_i-1
            # If we get here just return the previous i
            return i
        if name == "King" or name == "Knight" or name == "Pawn":
            for piece in player_1_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    return False
            for piece in player_2_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    return False
            return True

    def check(self,tiles, player_1_pieces, player_2_pieces, player):
        #Get the position of the two kings on the gameboard:
        for piece in player_1_pieces:
            if piece.name == "King":
                king_1_pos = piece.current_position
        for piece in player_2_pieces:
            if piece.name == "King":
                king_2_pos = piece.current_position

        #Iterate through all of the pieces moves to see if the king is in check.
        if player == 1:
            for piece in player_1_pieces:
                if king_2_pos in piece.calculate_moves(tiles, player_1_pieces, player_2_pieces):
                    return True
        if player == 2:
            for piece in player_2_pieces:
                if king_1_pos in piece.calculate_moves(tiles, player_1_pieces, player_2_pieces):
                    return True
        return False

    def checkmate(self, tiles, player_1_pieces, player_2_pieces, player):
        #A king is in checkmate if it does not have any moves that will move it safety
        # and no other pieces can block the piece or pieces inducing check.

        #Another way of thinking... If i calculate potential moves for every move i can make and my
        #king is still in danger, checkmate applies.
        #Player is the game player that induced check:
        copy_1 = copy.deepcopy(player_1_pieces)
        copy_2 = copy.deepcopy(player_2_pieces)
        if player == 1:
           for piece in copy_2:
               piece.calculate_moves(tiles, copy_1, copy_2)
               original_position = piece.current_position
               for move in range(len(piece.potential_moves)):
                   piece.move_piece(tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                    tiles,copy_1, copy_2)
                   if(not self.check(tiles, copy_1, copy_2, 1)):
                       print(piece.name)
                       print(piece.current_position)
                       print("not checkmate")
                       return False
                   piece.current_position = original_position
                   del copy_1
                   copy_1 = copy.deepcopy(player_1_pieces)
                   
        if player == 2:
           for piece in copy_1:
               piece.calculate_moves(tiles, copy_1, copy_2)
               original_position = piece.current_position
               for move in range(len(piece.potential_moves)):
                   piece.move_piece(tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                    tiles,copy_1, copy_2)
                   if(not self.check(tiles, copy_1, copy_2, 2)):
                       print(piece.name)
                       print(piece.current_position)
                       print("not checkmate")
                       return False
                   piece.current_position = original_position
                   del copy_2
                   copy_2 = copy.deepcopy(player_2_pieces)
        print("checkmate")
        return True
            
                          
    def calculate_moves(self, tiles, player_1_pieces, player_2_pieces):
        potential_moves = []
        cur = self.current_position
        if self.name == "Pawn":
            change = False
            if self.player == 1:
                if cur == self.starting_position:
                    if self.get_piece_on_tile(adder(cur,[1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[1,0]))
                    if self.get_piece_on_tile(adder(cur,[2,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[2,0]))
                        change = True
                else:
                    if self.get_piece_on_tile(adder(cur,[1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[1,0]))
                    if self.get_piece_on_tile(adder(cur, [1,1]), player_1_pieces, player_2_pieces) != None:
                        if(self.get_piece_on_tile(adder(cur, [1,1]), player_1_pieces, player_2_pieces).player == 2):
                            potential_moves.append(adder(cur,[1,1]))
                    if self.get_piece_on_tile(adder(cur, [1,-1]), player_1_pieces, player_2_pieces) != None:
                        if(self.get_piece_on_tile(adder(cur, [1,-1]), player_1_pieces, player_2_pieces).player == 2):
                            potential_moves.append(adder(cur,[1,-1]))
                            
                #Check for possible en passants:
                    right_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if right_piece != None:
                        print("1")
                        if((right_piece.player == 2) and (right_piece.name == "Pawn")):
                            print("2")
                            print(right_piece.en_passant)
                            #Bug where right_piece.en_passant = False
                            #This occurs because we calculate the moves for every piece.
                            if right_piece.en_passant == True:
                                print("3")
                                potential_moves.append(adder(cur,[1,1]))
                                
                    left_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if left_piece != None:
                        print("1")
                        if((left_piece.player == 2) and (left_piece.name == "Pawn")):
                            print("2")
                            if left_piece.en_passant == True:
                                print("3")
                                potential_moves.append(adder(cur,[1,-1]))
                                
                if change == False:
                    self.en_passant = False
                else:
                    self.en_passant = True
                    
            if self.player == 2:
                if cur == self.starting_position:
                    if self.get_piece_on_tile(adder(cur,[-1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-1,0]))
                    if self.get_piece_on_tile(adder(cur,[-2,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-2,0]))
                        change = True
                else:
                    if self.get_piece_on_tile(adder(cur,[-1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-1,0]))
                    if self.get_piece_on_tile(adder(cur, [-1,1]), player_1_pieces, player_2_pieces) != None:
                        if(self.get_piece_on_tile(adder(cur, [-1,1]), player_1_pieces, player_2_pieces).player == 1):
                            potential_moves.append(adder(cur,[-1,1]))
                    if self.get_piece_on_tile(adder(cur, [-1,-1]), player_1_pieces, player_2_pieces) != None:
                        if(self.get_piece_on_tile(adder(cur, [-1,-1]), player_1_pieces, player_2_pieces).player == 1):
                            potential_moves.append(adder(cur,[-1,-1]))

                #Check for possible en passants:
                    right_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if right_piece != None:
                        if((right_piece.player == 1) and (right_piece.name == "Pawn")):
                            if right_piece.en_passant == True:
                                potential_moves.append(adder(cur,[-1,1]))
                                
                    left_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if left_piece != None:
                        if((left_piece.player == 1) and (left_piece.name == "Pawn")):
                            if left_piece.en_passant == True:
                                potential_moves.append(adder(cur,[-1,-1]))

                if change == False:
                    self.en_passant = False
                else:
                    self.en_passant = True
                
        if self.name == "Knight":
                moves_to_check = [adder(cur,[1,-2]),adder(cur,[2,-1]),adder(cur,[2,1]),
                                  adder(cur,[1,2]),adder(cur,[-1,2]),adder(cur,[-2,1]),
                                  adder(cur,[-2,-1]),adder(cur,[-1,-2])]
                for move in moves_to_check:
                    if(move[1] <= (move[1] + 2) and (move[1] >= (move[1] - 2))):
                        if (self.empty_square(move, player_1_pieces, player_2_pieces, 0, 0)):
                            potential_moves.append(move)

        if self.name == "Bishop":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),-(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),(i+1)]))

        if self.name == "Rook":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[0,-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[0,-(i+1)]))
                    break
                if(opensquares == cur[1]):
                    break
                potential_moves.append(adder(cur,[0,-(i+1)]))
            for i in range(7 - cur[1]):
                opensquares = self.empty_square(adder(cur,[0,(i+1)]), player_1_pieces, player_2_pieces, i, 7 - cur[1])
                if(opensquares == 7 - cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[0,(i+1)]))
                    break
                potential_moves.append(adder(cur,[0,(i+1)]))
            for i in range(cur[0]):
                opensquares = self.empty_square(adder(cur,[-(i+1),0]), player_1_pieces, player_2_pieces, i, cur[0])
                if(opensquares == cur[0]):
                    break
                if(opensquares == cur[0]-1):
                    potential_moves.append(adder(cur,[-(i+1),0]))
                    break
                potential_moves.append(adder(cur,[-(i+1),0]))
            for i in range(7 - cur[0]):
                opensquares = self.empty_square(adder(cur,[(i+1),0]), player_1_pieces, player_2_pieces, i, 7 - cur[0])
                if(opensquares == 7 - cur[0]):
                    break
                if(opensquares == 7-cur[0]-1):
                    potential_moves.append(adder(cur,[(i+1),0]))
                    break
                potential_moves.append(adder(cur,[(i+1),0]))

        if self.name == "Queen":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),-(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),(i+1)]))


            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[0,-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[0,-(i+1)]))
                    break
                if(opensquares == cur[1]):
                    break
                potential_moves.append(adder(cur,[0,-(i+1)]))
            for i in range(7 - cur[1]):
                opensquares = self.empty_square(adder(cur,[0,(i+1)]), player_1_pieces, player_2_pieces, i, 7 - cur[1])
                if(opensquares == 7 - cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[0,(i+1)]))
                    break
                potential_moves.append(adder(cur,[0,(i+1)]))
            for i in range(cur[0]):
                opensquares = self.empty_square(adder(cur,[-(i+1),0]), player_1_pieces, player_2_pieces, i, cur[0])
                if(opensquares == cur[0]):
                    break
                if(opensquares == cur[0]-1):
                    potential_moves.append(adder(cur,[-(i+1),0]))
                    break
                potential_moves.append(adder(cur,[-(i+1),0]))
            for i in range(7 - cur[0]):
                opensquares = self.empty_square(adder(cur,[(i+1),0]), player_1_pieces, player_2_pieces, i, 7 - cur[0])
                if(opensquares == 7 - cur[0]):
                    break
                if(opensquares == 7-cur[0]-1):
                    potential_moves.append(adder(cur,[(i+1),0]))
                    break
                potential_moves.append(adder(cur,[(i+1),0]))

                
        if self.name == "King":
            if self.empty_square(adder(cur,[1,0]), player_1_pieces, player_2_pieces, 0, 0):
                potential_moves.append(adder(cur,[1,0]))
            if self.empty_square(adder(cur,[-1,0]), player_1_pieces, player_2_pieces, 0, 0):
                potential_moves.append(adder(cur,[-1,0]))
            if(cur[1] != 7):
                if self.empty_square(adder(cur,[0,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[0,1]))
                if self.empty_square(adder(cur,[1,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[1,1]))
                if self.empty_square(adder(cur,[-1,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[-1,1]))
            if(cur[1] != 0):
                if self.empty_square(adder(cur,[0,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[0,-1]))
                if self.empty_square(adder(cur,[-1,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[-1,-1]))
                if self.empty_square(adder(cur,[1,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[1,-1]))
            #Perform castling logic
            if (self.castle_QS == True and
                self.empty_square(adder(cur,[0,1]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,2]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,3]), player_1_pieces, player_2_pieces, 0, 0) and
                not self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces) == None and
                self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces).name == "Rook" and
                self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces).player == self.player):
 
                potential_moves.append(adder(cur, [0, 2]))
                
            if (self.castle_KS == True and
                self.empty_square(adder(cur,[0,-1]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,-2]), player_1_pieces, player_2_pieces, 0, 0) and
                not self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces) == None and
                self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces).name == "Rook" and
                self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces).player == self.player):
                
                potential_moves.append(adder(cur, [0, -2]))
                 

        #This calls check which in turn calls calculate_moves so we have a recursive infinite loop
        self.potential_moves = potential_moves
        potential_moves = self.crop_potential_moves(tiles, player_1_pieces, player_2_pieces)
        return self.potential_moves


    # def move_piece(self, position_to_move_to):

    def move_piece(self, tile, tiles, player_1_pieces, player_2_pieces):
        painted_tile = None
        for i in range(len(player_1_pieces)):
            if player_1_pieces[i].current_position == tile.coordinate:
                del player_1_pieces[i]
                break
        for i in range(len(player_2_pieces)):
            if player_2_pieces[i].current_position == tile.coordinate:
                del player_2_pieces[i]
                break
            
        if self.name == "King":
            
            self.castle_QS = False
            self.castle_KS = False

            if(tile.coordinate[1]-self.current_position[1] < -1):
                #Kingside castle
                piece = self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]-1],
                                        player_1_pieces, player_2_pieces)
                if piece != None:
                    self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]-1],
                                        player_1_pieces, player_2_pieces).current_position = [tile.coordinate[0], tile.coordinate[1]+1]
                    #GameBoard.paint_corner([tile.coordinate[0],0])
                    painted_tile = [tile.coordinate[0],0]
                    
            if(self.current_position[1] - tile.coordinate[1] < -1):
                #Queenside castle
                piece = self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]+2],
                                        player_1_pieces, player_2_pieces)
                if piece != None:
                    self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]+2],
                                        player_1_pieces, player_2_pieces).current_position = [tile.coordinate[0], tile.coordinate[1]-1]
                    #GameBoard.paint_corner([tile.coordinate[0],7])
                    painted_tile = [tile.coordinate[0],7]
                    
        if self.name == "Rook":
            if self.sub_name == "QS":
                for i in range(len(player_1_pieces)):
                    if (player_1_pieces[i].name == "King" and
                        player_1_pieces[i].player == self.player):
                        player_1_pieces[i].castle_QS = False
                        break
                for i in range(len(player_2_pieces)):
                    if (player_2_pieces[i].name == "King" and
                        player_2_pieces[i].player == self.player):
                        player_2_pieces[i].castle_QS = False
                        break
            if self.sub_name == "KS":
                for i in range(len(player_1_pieces)):
                    if (player_1_pieces[i].name == "King" and
                        player_1_pieces[i].player == self.player):
                        player_1_pieces[i].castle_KS = False
                        break
                for i in range(len(player_2_pieces)):
                    if (player_2_pieces[i].name == "King" and
                        player_2_pieces[i].player == self.player):
                        player_2_pieces[i].castle_KS = False
                        break
        self.current_position = tile.coordinate
        #self.check(player_1_pieces, player_2_pieces)
        return painted_tile

# Helper function for adding two arrays:
def adder(array1, array2):
    return_array = []
    for i in range(min(len(array1), len(array2))):
        return_array.append(array1[i] + array2[i])
    return return_array
        