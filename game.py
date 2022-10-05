from collections import Counter
import random
import pyinputplus as pyip

class rules:
    def __init__(self):
        self.dice = []
        self.scored_dice = []
        # start of game, everything is valid
        self.reroll = [1,1,1,1,1,1] # 1 means we can roll that die
        self.reset_dice = False
        self.new_turn = False
        self.sixreroll = False # to check if we rerolled with a 6
        self.running_score = 0
        self.player_list = []
        self.current_player_index = 0
        self.turn_count = 0
        self.highest_score = 0
        self.game_over = False
    
    
    def main(self,player_count):
        
        for i in range(player_count):
            name = "Player" + str(i+1)
            self.player_list.append([name,0])
        # print(self.player_list)
        #self.turn()
        
    def randomize_dice(self):
        """
        Randomize dice, ignore frozen (marked as 0)
        """
        temp_dice = self.dice

        self.dice = []
        for i in range(6):
            if self.reroll[i] == 1:
                self.dice.append(random.randint(1,6)) # randomize unfrozen dice
            else:
                self.dice.append(temp_dice[i]) # put frozen dice back in list
                
    def score_roll(self,roll):
        """
        score the dice
        1 = 100
        5 = 50
        Triples = number * 100 (Ex. 4,4,4 = 400)
        4x = triple * 2
        5x = 4x * 2
        6x = 5x * 2
        Triple 1 = 1000
        3 pair = 1000
        Everything else = 0
        """
        dice_to_score = roll
        
        count = Counter(dice_to_score)
        score = 0
        double_count = 0
        if len(dice_to_score) > 0:
            for i in range(1,7):
                if count[i] >= 3:
                    if i == 1:
                        score += 1000 * (2**(count[i]-3)) # multiple 1s
                    else:
                        score += (i*100) * (2**(count[i]-3)) # multiple of any number
                if count[i] == 2:
                    double_count += 1
                    if double_count == 3:
                        score += 1000

            for i in range(len(dice_to_score)):
                
                if double_count != 3:
                    if count[dice_to_score[i]] < 3:
                        if dice_to_score[i] == 1:
                            score += 100
                        elif dice_to_score[i] == 5:
                            score += 50
                        else:
                            score += 0       
         
        #print(score)
        return score

            
    
    
    def valid_move(self,frozen):
        '''
        player chooses which dice they want to freeze, 0 is frozen 1 is not
        all dice removed must score, so:
        1's
        5's
        multiples >= 3
        3 pair

        return if it's valid
        '''
        count_player_frozen = Counter(frozen)
        count_game_frozen = Counter(self.reroll)
        
        
        if count_player_frozen[0] <= count_game_frozen[0]:
            return False
        else:
            just_frozen = []
            for i,game_die in enumerate(self.reroll):
                # if the die is already frozen, it should also be frozen in player's entry
                if game_die == 0 and frozen[i] != 0:
                    return False 
                elif game_die == 1 and frozen[i] == 0: # if the die was just frozen, append it to the list
                    #print(frozen, self.dice)
                    just_frozen.append(self.dice[i])
        
        count = Counter(just_frozen)
        self.scored_dice = just_frozen
        
        if count_game_frozen[0] == 5 and count_player_frozen[0] == 6:
            if just_frozen[0] == 6:       # if last die was a 6 also valid
                self.sixreroll = True
                return True
        
        if len(just_frozen) == 6:  # check if it's 3 pairs
            double_count = 0
            for i in range(1,7):
                if count[i] == 2:
                    double_count += 1
            if double_count == 3:
                return True
        
        if len(just_frozen) >=3:
            
            if count.most_common()[0][1] == len(just_frozen):
                return True
            elif count.most_common()[1][1] == 3:
                if (count.most_common()[1][1] + count.most_common()[0][1]) == len(just_frozen):
                    return True
            else:
                if count.most_common()[0][1] >= 3:
                    num = 0
                    test = 0
                    for i in range(len(just_frozen)):
                        if just_frozen[i] != count.most_common()[0][0]: # if it's not the most common number
                            #print(just_frozen[i])
                            num += 1
                            if (just_frozen[i] == 1 or just_frozen[i] == 5): # if it is a 1 or 5
                                test += 1 
                                
                    if num == test: # check if all of the rest are 1's or 5's
                        return True
                    else: 
                        return False
        else:
            test = 0
            for i in range(len(just_frozen)):
                if just_frozen[i] != 1 and just_frozen[i] != 5:
                    pass
                else:
                    test += 1
            if test == len(just_frozen):
                return True
            else:
                return False
            
    def turn(self):
        self.new_turn = False
        self.keep_score = False
        
        if self.running_score > 0:
                response = input()
                if response[7] == "1": # 0 to keep going, 1 to reset
                    self.reroll = [1,1,1,1,1,1]
                    self.running_score = 0
        
        while not self.new_turn:
            
            
            print(self.reroll)
            self.randomize_dice()
            print(self.dice)
            
            frozen = []
            x = input()
            for num in range(len(x)-1):
                frozen.append(int(x[num]))
            
            if x[6] == "0": # 0 to end turn, 1 to keep going
                self.keep_score = True
                
            valid = self.valid_move(frozen)
        
            if valid:
                if not self.keep_score: # If not ending rolling
                    score = self.score_roll(self.scored_dice)
                    self.reroll = frozen
                    if self.reroll == [0,0,0,0,0,0]: # if used all the dice
                        self.reset_dice = True
                    if score != "Farkle" and not self.sixreroll: # add to running score
                        self.running_score += score
                    elif score == "Farkle": # if farkle, reset the dice and end turn
                        self.running_score = 0
                        self.reroll = [1,1,1,1,1,1]
                        self.new_turn = True
                    if self.reset_dice: 
                        self.reroll = [1,1,1,1,1,1] # reset the dice
                        self.sixreroll = False
                    print(self.dice, self.scored_dice,self.running_score)
                else: # if ending rolling for turn
                    score = self.score_roll(self.scored_dice)
                    if score != "Farkle": # just in case you did farkle
                        self.running_score += score
                    self.player_list[self.current_player_index][1] += self.running_score # add the score to player's score
                    if self.player_list[self.current_player_index][1] > self.highest_score: # get the highest score
                        self.highest_score = self.player_list[self.current_player_index][1]
                    self.reroll = frozen
                    self.keep_score = False
                    self.new_turn = True
            else:
                self.running_score = 0
                self.reroll = [1,1,1,1,1,1]
                self.new_turn = True
        if self.highest_score >= 10000: # someone won
            self.game_over = True
        if self.current_player_index != (len(self.player_list)-1): # if it isn't the last player
            self.current_player_index += 1
            print(self.player_list)
        else: # if it is the last player
            self.current_player_index = 0
            self.turn_count += 1
            print(self.player_list)
        if not self.game_over: self.turn()
    
    def AI_play_step(self,move):
        reward = 0
        # if self.turn_length == 0:
            
        #     if self.running_score > 0:
        #         response = move
        #         if response[7] == "1": # 0 to keep going, 1 to reset
        #             self.reroll = [1,1,1,1,1,1]
        #             self.running_score = 0
        #     self.turn_length += 1
            
        if self.turn_length >= 0:
            
            self.randomize_dice()
            
            frozen = []
            x = move
            for num in range(6):
                frozen.append(int(x[num]))
            
            if x[6] == "0": # 0 to end turn, 1 to keep going
                self.keep_score = True
                
            valid = self.valid_move(frozen)
        
            if valid:
                if not self.keep_score: # If not ending rolling
                    score = self.score_roll(self.scored_dice)
                    self.reroll = frozen
                    if self.reroll == [0,0,0,0,0,0]: # if used all the dice
                        self.reset_dice = True
                    if score != "Farkle" and not self.sixreroll: # add to running score
                        self.running_score += score
                        reward = score
                    if self.reset_dice: 
                        self.reroll = [1,1,1,1,1,1] # reset the dice
                        self.sixreroll = False
                        reward += 100
                    
                else: # if ending rolling for turn
                    score = self.score_roll(self.scored_dice)
                    self.running_score += score
                    self.player_list[self.current_player_index][1] += self.running_score # add the score to player's score
                    reward = self.player_list[self.current_player_index][1]
                    if self.player_list[self.current_player_index][1] > self.highest_score: # get the highest score
                        self.highest_score = self.player_list[self.current_player_index][1]
                    self.reroll = frozen
                    self.keep_score = False
                    self.new_turn = True
                    self.turn_length = 0
                    # for taking out the running score aspect
                    self.running_score = 0
                    self.reroll = [1,1,1,1,1,1]
                score = self.player_list[self.current_player_index][1]
                
            else:
                self.running_score = 0
                self.reroll = [1,1,1,1,1,1]
                self.new_turn = True
                self.turn_length = 0
                reward = -50
                score = self.player_list[self.current_player_index][1]
                if self.highest_score >= 10000: # someone won
                    self.game_over = True
                if self.current_player_index != (len(self.player_list)-1): # if it isn't the last player
                    self.current_player_index += 1
                elif self.current_player_index == (len(self.player_list)-1): # if it is the last player
                    self.current_player_index = 0
                    self.turn_count += 1
        
        return reward, self.game_over, self.turn_count
    
    def reset(self,player_count):
        self.dice = []
        self.randomize_dice()
        self.scored_dice = []
        # start of game, everything is valid
        self.reroll = [1,1,1,1,1,1] # 1 means we can roll that die
        self.reset_dice = False
        self.new_turn = False
        self.sixreroll = False # to check if we rerolled with a 6
        self.running_score = 0
        self.keep_score = False
        self.player_list = []
        self.current_player_index = 0
        self.turn_count = 0
        self.highest_score = 0
        self.game_over = False
        self.times_needed_help = 0
        for i in range(player_count):
            name = "Player" + str(i+1)
            self.player_list.append([name,0])
        self.turn_length = 0
            

#rules.main(rules(),2)

