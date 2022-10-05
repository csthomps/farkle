import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
from game import rules
import random
import numpy as np
from collections import deque
import itertools

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = 'fun_projects/farkle/model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

class Agent():
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(14, 5000, 128)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
    
    def get_state(self,game):
        new_turn = game.turn_length
        running_score = game.running_score
        dice = game.dice
        reroll = game.reroll
        
        state = [
            new_turn,
            running_score,
            dice[0],
            dice[1],
            dice[2],
            dice[3],
            dice[4],
            dice[5],
            reroll[0],
            reroll[1],
            reroll[2],
            reroll[3],
            reroll[4],
            reroll[5]
        ]
        return np.array(state, dtype=int)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
        
    
    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        #final_move = []
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 127)
            #final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.any(prediction).item()
            #final_move[move] = 1

        return move #final_move
def train():
    # plot_scores = []
    # plot_mean_scores = []
    # total_score = 0
    record = 1000
    agent = Agent()
    game = rules()
    game.reset(5)
    
    final_move_list = []
    total_count = 0
    for numbers in itertools.product([0,1],repeat=7):
        final_move_list.append(numbers)
    
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        move = agent.get_action(state_old)
        final_move = final_move_list[move]
        
        final_move = str(final_move)
        final_move = final_move.replace(", ","") # fixing output
        final_move = final_move.replace(")","")
        final_move = final_move.replace("(","")
        
        #print(final_move)
        
        # perform move and get new state
        reward, done, turn_count = game.AI_play_step(final_move)
        #print(game.dice,final_move,game.turn_length)
        #print(reward)
        state_new = agent.get_state(game)

        # train short memory
        final_move = int(final_move) # make the string into integer
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            # train long memory, plot result
            print(game.player_list)
            game.reset(5)
            agent.n_games += 1
            agent.train_long_memory()

            if turn_count < record:
                record = turn_count
                agent.model.save()


            #plot_scores.append(turn_count)
            total_count += turn_count
            mean_turn_count = total_count / agent.n_games
            #plot_mean_scores.append(mean_turn_count)
        #    plot(plot_scores, plot_mean_scores)
            print('Game', agent.n_games, 'Turn Count:', turn_count, "| Average:", round(mean_turn_count,2))
            


if __name__ == '__main__':
    train()