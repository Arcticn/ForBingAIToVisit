# -*- coding: utf-8 -*-
import json
import random
import time

# 定义棋盘大小
BOARD_SIZE = 11

# 定义棋子类型
EMPTY = 0
HUMAN = 1
COMPUTER = 2

# 定义方向向量
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

# 定义蒙特卡罗树搜索的次数
MCTS_TIMES = 100

# 定义启发式a-β剪枝搜索的深度
AB_DEPTH = 3

# 定义启发式评估函数的权重
WEIGHTS = [0, 1, 10, 1000]

# 定义无穷大和无穷小值
INF = float("inf")
NEG_INF = float("-inf")

# 定义时间限制（秒）
TIME_LIMIT = 5.5

# 定义棋盘类
class Board:
    # 初始化棋盘
    def __init__(self):
        # 创建一个二维数组来存储棋盘状态
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # 创建一个集合来存储空位置
        self.empty_positions = set()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.empty_positions.add((i, j))
        # 创建一个字典来存储每个位置的禁入点情况
        self.forbidden_points = {}
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.forbidden_points[(i, j)] = [False, False]
    
    # 复制棋盘
    def copy(self):
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        new_board.empty_positions = self.empty_positions.copy()
        new_board.forbidden_points = self.forbidden_points.copy()
        return new_board
    
    # 判断位置是否在棋盘内
    def is_in_board(self, x, y):
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    
    # 判断位置是否为空
    def is_empty(self, x, y):
        return self.board[x][y] == EMPTY
    
    # 判断位置是否为禁入点（对于某一方）
    def is_forbidden(self, x, y, player):
        return self.forbidden_points[(x, y)][player - 1]
    
    # 落子（假设位置合法）
    def place(self, x, y, player):
        # 更新棋盘状态
        self.board[x][y] = player
        # 移除空位置集合中的该位置
        self.empty_positions.remove((x, y))
        # 更新禁入点情况（对于双方）
        for dx, dy in DIRECTIONS:
            nx = x + dx * 3
            ny = y + dy * 3
            if self.is_in_board(nx, ny) and self.board[nx][ny] == player:
                mx = x + dx * 2
                my = y + dy * 2
                if self.is_in_board(mx, my) and self.board[mx][my] == player:
                    lx = x + dx
                    ly = y + dy
                    if self.is_in_board(lx, ly) and self.board[lx][ly] == player:
                        # 如果在一个方向上连成四个，那么该位置是自己的禁入点，也是对方的禁入点（如果对方下了就输了）
                        self.forbidden_points[(x, y)][player - 1] = True
                        self.forbidden_points[(x, y)][2 - player] = True
    
    # 撤销落子（假设位置合法）
    def undo(self, x, y, player):
        # 更新棋盘状态
        self.board[x][y] = EMPTY
        # 添加空位置集合中的该位置
        self.empty_positions.add((x, y))
        # 更新禁入点情况（对于双方）
        for dx, dy in DIRECTIONS:
            nx = x + dx * 3
            ny = y + dy * 3
            if self.is_in_board(nx, ny) and self.board[nx][ny] == player:
                mx = x + dx * 2
                my = y + dy * 2
                if self.is_in_board(mx, my) and self.board[mx][my] == player:
                    lx = x + dx
                    ly = y + dy
                    if self.is_in_board(lx, ly) and self.board[lx][ly] == player:
                        # 如果在一个方向上连成四个，那么该位置是自己的禁入点，也是对方的禁入点（如果对方下了就输了）
                        self.forbidden_points[(x, y)][player - 1] = False
                        self.forbidden_points[(x, y)][2 - player] = False
    
    # 判断游戏是否结束（假设最后一步是player落子）
    def is_over(self, x, y, player):
        # 如果棋盘已满，游戏结束，平局
        if len(self.empty_positions) == 0:
            return True
        # 如果最后一步是禁入点，游戏结束，player输了
        if self.is_forbidden(x, y, player):
            return True
        # 如果最后一步让对方连成四个，游戏结束，player赢了
        for dx, dy in DIRECTIONS:
            count = 0
            for i in range(1, 5):
                nx = x + dx * i
                ny = y + dy * i
                if self.is_in_board(nx, ny) and self.board[nx][ny] == 2 - player:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                nx = x - dx * i
                ny = y - dy * i
                if self.is_in_board(nx, ny) and self.board[nx][ny] == 2 - player:
                    count += 1
                else:
                    break
            if count >= 4:
                return True
        # 否则游戏未结束
        return False
    
    # 启发式评估函数（对于某一方）
    def evaluate(self, player):
        # 初始化评估值为0
        score = 0
        # 遍历棋盘上的每个位置
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                # 如果该位置为空，跳过
                if self.board[i][j] == EMPTY:
                    continue
                # 如果该位置是自己的棋子，加分；如果是对方的棋子，减分
                factor = WEIGHTS[1] if self.board[i][j] == player else -WEIGHTS[1]
                # 在四个方向上统计连续的棋子数目，并根据权重加减分数
                for dx, dy in DIRECTIONS:
                    count = 0
                    for k in range(1, 5):
                        nx = i + dx * k
                        ny = j + dy * k
                        if self.is_in_board(nx, ny) and self.board[nx][ny] == self.board[i][j]:
                            count += 1
                        else:
                            break
                    # 根据连续的棋子数目，乘以相应的权重，加减分数
                    score += factor * WEIGHTS[count]
        # 返回评估值
        return score
    
    # 启发式a-β剪枝搜索（对于某一方）
    def alpha_beta_search(self, player, depth, alpha, beta):
        # 如果搜索深度为0，或者游戏已经结束，返回当前的评估值
        if depth == 0 or self.is_over():
            return self.evaluate(player)
        # 如果是自己的回合，寻找最大值
        if player == COMPUTER:
            # 初始化最大值为无穷小
            max_value = NEG_INF
            # 遍历所有可用的位置
            for x, y in self.empty_positions:
                # 如果该位置是禁入点，跳过
                if self.is_forbidden(x, y, player):
                    continue
                # 在该位置落子
                self.place(x, y, player)
                # 递归地搜索下一层，并更新最大值和alpha值
                value = self.alpha_beta_search(2 - player, depth - 1, alpha, beta)
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                # 撤销落子
                self.undo(x, y, player)
                # 如果alpha大于等于beta，剪枝
                if alpha >= beta:
                    break
            # 返回最大值
            return max_value
        # 如果是对方的回合，寻找最小值
        else:
            # 初始化最小值为无穷大
            min_value = INF
            # 遍历所有可用的位置
            for x, y in self.empty_positions:
                # 如果该位置是禁入点，跳过
                if self.is_forbidden(x, y, player):
                    continue
                # 在该位置落子
                self.place(x, y, player)
                # 递归地搜索下一层，并更新最小值和beta值
                value = self.alpha_beta_search(2 - player, depth - 1, alpha, beta)
                min_value = min(min_value, value)
                beta = min(beta, value)
                # 撤销落子
                self.undo(x, y, player)
                # 如果alpha大于等于beta，剪枝
                if alpha >= beta:
                    break
            # 返回最小值
            return min_value
    
    # 蒙特卡罗树搜索（对于某一方）
    def monte_carlo_tree_search(self, player):
        # 初始化最佳位置为None
        best_position = None
        # 初始化最大胜率为0
        max_win_rate = 0
        # 遍历所有可用的位置
        for x, y in self.empty_positions:
            # 如果该位置是禁入点，跳过
            if self.is_forbidden(x, y, player):
                continue
            # 初始化胜利次数和模拟次数为0
            win_count = 0
            sim_count = 0
            # 重复蒙特卡罗树搜索的次数
            for _ in range(MCTS_TIMES):
                # 复制当前的棋盘状态
                board_copy = self.copy()
                # 在该位置落子
                board_copy.place(x, y, player)
                # 随机模拟游戏直到结束，并记录胜利次数和模拟次数
                winner = board_copy.random_play(2 - player)
                if winner == player:
                    win_count += 1
                sim_count += 1
            # 计算该位置的胜率，并更新最佳位置和最大胜率
            win_rate = win_count / sim_count
            if win_rate > max_win_rate:
                best_position = (x, y)
                max_win_rate = win_rate
        # 返回最佳位置
        return best_position
    
    # 随机模拟游戏直到结束（假设最后一步是player落子）
    def random_play(self, player):
        # 如果游戏已经结束，返回胜利者（如果平局，返回None）
        if self.is_over():
            return self.get_winner()
        # 随机选择一个可用的位置，并在该位置落子
        x, y = random.choice(list(self.empty_positions))
        self.place(x, y, player)
        # 递归地模拟下一步，并返回胜利者（如果平局，返回None）
        return self.random_play(2 - player)
    
    # 获取胜利者（假设游戏已经结束）
    def get_winner(self):
        # 如果棋盘已满，平局，返回None
        if len(self.empty_positions) == 0:
            return None
        # 遍历棋盘上的每个位置，判断是否有连成四个的情况，如果有，返回对应的玩家，如果没有，返回None
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] != EMPTY:
                    for dx, dy in DIRECTIONS:
                        count = 0
                        for k in range(1, 5):
                            nx = i + dx * k
                            ny = j + dy * k
                            if self.is_in_board(nx, ny) and self.board[nx][ny] == self.board[i][j]:
                                count += 1
                            else:
                                break
                        if count >= 4:
                            return self.board[i][j]
        return None

    # 获取电脑的落子位置（假设电脑是先手或后手）
    def get_computer_move(self, first):
        # 如果电脑是先手，且棋盘为空，那么随机选择一个角落
        if first and len(self.empty_positions) == BOARD_SIZE * BOARD_SIZE:
            return random.choice([(0, 0), (0, BOARD_SIZE - 1), (BOARD_SIZE - 1, 0), (BOARD_SIZE - 1, BOARD_SIZE - 1)])
        # 如果电脑是后手，且棋盘只有一个棋子，那么随机选择一个相邻的位置
        if not first and len(self.empty_positions) == BOARD_SIZE * BOARD_SIZE - 1:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if self.board[i][j] != EMPTY:
                        x = i
                        y = j
                        break
            return random.choice([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])
        # 否则，使用混合的搜索策略，先用蒙特卡罗树搜索找到一个候选位置，再用启发式a-β剪枝搜索评估每个可用位置的分数，选择最高分的位置
        else:
            # 使用蒙特卡罗树搜索找到一个候选位置
            candidate = self.monte_carlo_tree_search(COMPUTER)
            # 初始化最佳位置为候选位置
            best_position = candidate
            # 初始化最高分为无穷小
            max_score = NEG_INF
            # 记录开始时间
            start_time = time.time()
            # 遍历所有可用的位置
            for x, y in self.empty_positions:
                # 如果该位置是禁入点，跳过
                if self.is_forbidden(x, y, COMPUTER):
                    continue
                # 在该位置落子
                self.place(x, y, COMPUTER)
                # 使用启发式a-β剪枝搜索评估该位置的分数，并更新最佳位置和最高分
                score = self.alpha_beta_search(HUMAN, AB_DEPTH, NEG_INF, INF)
                if score > max_score:
                    best_position = (x, y)
                    max_score = score
                # 撤销落子
                self.undo(x, y, COMPUTER)
                # 记录当前时间
                current_time = time.time()
                # 如果已经超过时间限制，停止搜索，并返回最佳位置（如果没有找到更好的位置，返回候选位置）
                if current_time - start_time > TIME_LIMIT:
                    break
            return best_position

# 定义主函数
def main():
    # 创建一个棋盘对象
    board = Board()
    # 读取Json输入，获取历史棋步
    full_input = json.loads(input())
    all_requests = full_input["requests"]
    all_responses = full_input["responses"]
    # 判断电脑是先手还是后手（如果电脑是先手，第一个回合输入的"requests"为{"x": -1, "y": -1 }）
    first = all_requests[0]["x"] == -1 and all_requests[0]["y"] == -1
    # 根据历史棋步还原棋盘状态，并判断当前回合是谁的回合（如果是电脑的回合，那么"requests"和"responses"的长度相等）
    turn = COMPUTER
    for i in range(len(all_responses)-1):
        myInput = all_requests[i]
        myOutput = all_responses[i]
        if myInput["x"] >= 0 and myInput["y"] >= 0:
            board.place(myInput["x"], myInput["y"], HUMAN)
        if myOutput["x"] >= 0 and myOutput["y"] >= 0:
            board.place(myOutput["x"], myOutput["y"], COMPUTER)

    myInput = all_requests[-1]
    if myInput["x"] >= 0 and myInput["y"] >= 0:
        board.place(myInput["x"], myInput["y"], HUMAN)
    # 如果当前回合是电脑的回合，获取电脑的落子位置，并构造Json输出
    if turn == COMPUTER:
        x, y = board.get_computer_move(first)
        print(json.dumps({"response": {"x": x, "y": y}}))

# 运行主函数
if __name__ == "__main__":
    main()
