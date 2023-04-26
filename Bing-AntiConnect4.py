# -*- coding: utf-8 -*-
# This is a program for playing reverse connect four with human
# Reverse connect four is a variant of connect four where the goal is to make the opponent connect four pieces
# The program uses Monte Carlo tree search algorithm to select the best move and alpha-beta pruning algorithm to evaluate the board state
# The program uses json module to handle input and output, numpy module to represent the board matrix, random module to generate random numbers
# The program uses time module to control the time limit for each move
# The program can adapt to different first-hand situations by checking the first request

import json
import numpy as np
import random
import time

# Define some constants
BOARD_SIZE = 11 # The size of the board
EMPTY = 0 # The value for empty cell
HUMAN = 1 # The value for human player
COMPUTER = 2 # The value for computer player
WIN = 1 # The value for win state
LOSE = -1 # The value for lose state
DRAW = 0 # The value for draw state
TIME_LIMIT = 5.5 # The time limit for each move in seconds

# Define a class for nodes in the Monte Carlo tree search
class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board # The board state of this node
        self.parent = parent # The parent node of this node
        self.move = move # The move that leads to this node from the parent node
        self.children = [] # The list of child nodes of this node
        self.visits = 0 # The number of visits of this node
        self.value = 0 # The total value of this node

    def is_leaf(self):
        # Return True if this node is a leaf node (no children)
        return len(self.children) == 0

    def is_root(self):
        # Return True if this node is a root node (no parent)
        return self.parent is None

    def expand(self):
        # Expand this node by generating all possible child nodes
        moves = get_valid_moves(self.board) # Get all valid moves for this node's board state
        for move in moves:
            child_board = make_move(self.board, move) # Make a move and get the new board state
            child_node = Node(child_board, self, move) # Create a new child node with the new board state, the current node as parent and the move as move
            self.children.append(child_node) # Add the child node to the list of children

    def select(self):
        # Select a child node with the highest UCB1 value
        best_value = -float('inf') # Initialize the best value as negative infinity
        best_child = None # Initialize the best child as None
        for child in self.children: # For each child node
            ucb1_value = child.get_ucb1_value() # Calculate the UCB1 value of the child node
            if ucb1_value > best_value: # If the UCB1 value is better than the best value so far
                best_value = ucb1_value # Update the best value
                best_child = child # Update the best child
        return best_child # Return the best child

    def update(self, result):
        # Update this node's visits and value with the given result (win, lose or draw)
        self.visits += 1 # Increment the visits by one
        self.value += result # Add the result to the value

    def get_ucb1_value(self):
        # Calculate and return the UCB1 value of this node
        c = np.sqrt(2) # Define a constant c as square root of 2 (can be tuned)
        exploitation_term = self.value / self.visits if self.visits > 0 else 0 # Calculate the exploitation term as the average value of this node if it has been visited, otherwise zero
        exploration_term = c * np.sqrt(np.log(self.parent.visits) / self.visits) if self.visits > 0 else float('inf') # Calculate the exploration term as c times square root of log of
        # the number of visits of this node over the number of visits of this node if it has been visited, otherwise infinity
        ucb1_value = exploitation_term + exploration_term # Calculate the UCB1 value as the sum of exploitation term and exploration term
        return ucb1_value # Return the UCB1 value

# Define a function to get the board state after making a move
def make_move(board, move):
    new_board = board.copy() # Make a copy of the board
    x, y = move['x'], move['y'] # Get the x and y coordinates of the move
    new_board[x][y] = get_current_player(board) # Set the cell at (x, y) to the current player's value
    return new_board # Return the new board

# Define a function to get the current player's value based on the board state
def get_current_player(board):
    count_human = np.count_nonzero(board == HUMAN) # Count the number of human pieces on the board
    count_computer = np.count_nonzero(board == COMPUTER) # Count the number of computer pieces on the board
    if count_human == count_computer: # If the number of human pieces is equal to the number of computer pieces
        return COMPUTER # The current player is computer
    else: # Otherwise
        return HUMAN # The current player is human

# Define a function to get all valid moves for a given board state
def get_valid_moves(board):
    valid_moves = [] # Initialize an empty list for valid moves
    for i in range(BOARD_SIZE): # For each row index
        for j in range(BOARD_SIZE): # For each column index
            if board[i][j] == EMPTY: # If the cell at (i, j) is empty
                valid_move = {'x': i, 'y': j} # Create a valid move with x and y coordinates
                valid_moves.append(valid_move) # Add the valid move to the list
    return valid_moves # Return the list of valid moves

# Define a function to check if a given board state is terminal (win, lose or draw)
def is_terminal(board):
    return get_board_value(board) != None # Return True if the board value is not None, otherwise False

# Define a function to get the board value (win, lose or draw) for a given board state
def get_board_value(board):
    for i in range(BOARD_SIZE): # For each row index
        for j in range(BOARD_SIZE): # For each column index
            if board[i][j] != EMPTY: # If the cell at (i, j) is not empty
                player = board[i][j] # Get the player's value at that cell
                if check_win(board, player, i, j): # If the player wins by placing a piece at that cell
                    return -WIN if player == COMPUTER else WIN # Return -WIN if the player is computer (bad for computer), otherwise WIN (good for computer)
    if np.count_nonzero(board == EMPTY) == 0: # If there are no empty cells on the board
        return DRAW # Return DRAW (neutral for computer)
    return None # Return None (not terminal)

# Define a function to check if a given player wins by placing a piece at a given cell on a given board state
def check_win(board, player, x, y):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # Define four directions to check: horizontal, vertical, diagonal and anti-diagonal
    for dx, dy in directions: # For each direction
        count = 1 # Initialize the count as one (the piece itself)
        for k in range(1, 4): # For each offset from 1 to 3
            i = x + k * dx # Calculate the row index of the adjacent cell in that direction with that offset
            j = y + k * dy # Calculate the column index of the adjacent cell in that direction with that offset
            if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and board[i][j] == player: # If the adjacent cell is within the board and has the same player's value
                count += 1 # Increment the count by one
            else: # Otherwise
                break # Break out of the loop
        for k in range(1, 4): # For each offset from 1 to 3
            i = x - k * dx # Calculate the row index of the adjacent cell in the opposite direction with that offset
            j = y - k * dy # Calculate the column index of the adjacent cell in the opposite direction with that offset
            if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and board[i][j] == player: # If the adjacent cell is within the board and has the same player's value
                count += 1 # Increment the count by one
            else: # Otherwise
                break # Break out of the loop
        if count >= 4: # If the count is at least four
            return True # Return True (the player wins)
    return False # Return False (the player does not win)

# Define a function to perform the Monte Carlo tree search and return the best move
def mcts(board):
    root = Node(board) # Create a root node with the given board state
    start_time = time.time() # Record the start time of the search
    while time.time() - start_time < TIME_LIMIT: # While the time limit is not exceeded
        node = root # Initialize the node as the root node
        while not node.is_leaf(): # While the node is not a leaf node
            node = node.select() # Select a child node with the highest UCB1 value
        if not is_terminal(node.board): # If the node's board state is not terminal
            node.expand() # Expand the node by generating all possible child nodes
        result = rollout(node.board) # Perform a random rollout from the node's board state and get the result (win, lose or draw)
        while node is not None: # While the node is not None
            node.update(result) # Update the node's visits and value with the result
            node = node.parent # Move to the parent node
    best_move = get_best_move(root) # Get the best move from the root node's children based on the most visits
    return best_move # Return the best move

# Define a function to perform a random rollout from a given board state and return the result (win, lose or draw)
def rollout(board):
    current_board = board.copy() # Make a copy of the board state
    while not is_terminal(current_board): # While the board state is not terminal
        moves = get_valid_moves(current_board) # Get all valid moves for the board state
        random_move = random.choice(moves) # Choose a random move from the list of valid moves
        current_board = make_move(current_board, random_move) # Make a random move and get the new board state
    return get_board_value(current_board) # Return the board value (win, lose or draw) for the final board state

# Define a function to get the best move from a list of nodes based on the most visits
def get_best_move(nodes):
    most_visits = -float('inf') # Initialize the most visits as negative infinity
    best_move = None # Initialize the best move as None
    for node in nodes: # For each node in the list of nodes
        if node.visits > most_visits: # If the node's visits is more than the most visits so far
            most_visits = node.visits # Update the most visits
            best_move = node.move # Update the best move
    return best_move # Return the best move

# Define a function to evaluate a board state using alpha-beta pruning algorithm and return a score (the higher, the better for computer)
def evaluate(board, depth, alpha, beta):
    if is_terminal(board): # If the board state is terminal
        return get_board_value(board) * (BOARD_SIZE ** 2 + 1 - depth) # Return the board value (win, lose or draw) times a weight based on the depth (the earlier, the better)
    if depth == 0: # If the depth limit is reached
        return 0 # Return zero (unknown)
    moves = get_valid_moves(board) # Get all valid moves for the board state
    if get_current_player(board) == COMPUTER: # If the current player is computer
        best_score = -float('inf') # Initialize the best score as negative infinity
        for move in moves: # For each move in the list of valid moves
            new_board = make_move(board, move) # Make a move and get the new board state
            score = evaluate(new_board, depth - 1, alpha, beta) # Recursively evaluate the new board state with a smaller depth and the same alpha and beta values
            best_score = max(best_score, score) # Update the best score with the maximum of the current best score and the new score
            alpha = max(alpha, best_score) # Update alpha with the maximum of the current alpha and the best score
            if beta <= alpha: # If beta is smaller than or equal to alpha
                break # Break out of the loop (beta cut-off)
        return best_score # Return the best score
    else: # If the current player is human
        best_score = float('inf') # Initialize the best score as positive infinity
        for move in moves: # For each move in the list of valid moves
            new_board = make_move(board, move) # Make a move and get the new board state
            score = evaluate(new_board, depth - 1, alpha, beta) # Recursively evaluate the new board state with a smaller depth and the same alpha and beta values
            best_score = min(best_score, score) # Update the best score with the minimum of the current best score and the new score
            beta = min(beta, best_score) # Update beta with the minimum of the current beta and the best score
            if beta <= alpha: # If beta is smaller than or equal to alpha
                break # Break out of the loop (alpha cut-off)
        return best_score # Return the best score

# Define a function to print a board state in a human-readable way
def print_board(board):
    print('  ', end='') # Print two spaces at the beginning of each row
    for j in range(BOARD_SIZE): # For each column index
        print(j, end=' ') # Print the column index with a space
    print() # Print a new line at the end of each row
    for i in range(BOARD_SIZE): # For each row index
        print(i, end=' ') # Print the row index with a space
        for j in range(BOARD_SIZE): # For each column index
            if board[i][j] == EMPTY: # If the cell at (i, j) is empty
                print('.', end=' ') # Print a dot with a space
            elif board[i][j] == HUMAN: # If the cell at (i, j) is human
                print('O', end=' ') # Print an O with a space
            elif board[i][j] == COMPUTER: # If the cell at (i, j) is computer
                print('X', end=' ') # Print an X with a space
        print() # Print a new line at the end of each row

# Define a function to get the initial board state
def get_initial_board():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int) # Create a board matrix filled with zeros
    return board # Return the board matrix

# Define a function to get the board state from the history of requests and responses
def get_board_from_history(requests, responses):
    board = get_initial_board() # Get the initial board state
    for i in range(len(requests)): # For each index in the history
        request = requests[i] # Get the request at that index
        if request['x'] >= 0 and request['y'] >= 0: # If the request is not the first move for computer
            board = make_move(board, request) # Make the request move and get the new board state
        if i >= len(responses):
            break
        response = responses[i] # Get the response at that index
        if response['x'] >= 0 and response['y'] >= 0: # If the response is not the first move for human
            board = make_move(board, response) # Make the response move and get the new board state
    return board # Return the final board state

# Define a function to play reverse connect four with human
def play():
    full_input = json.loads(input()) # Read the full input as json
    all_requests = full_input["requests"] # Get all requests from the input
    all_responses = full_input["responses"] # Get all responses from the input
    board = get_board_from_history(all_requests, all_responses) # Get the board state from the history of requests and responses
    if is_terminal(board): # If the board state is terminal
        print_board(board) # Print the board state
        print('Game over.') # Print game over message
        return # Return from the function
    move = mcts(board) # Perform the Monte Carlo tree search and get the best move
    response = {'response': move} # Create a response with the move
    print(json.dumps(response)) # Print the response as json

# Call the play function to start the game
play()
