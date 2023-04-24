# 反四子棋程序 by Bing
# 使用Python 3.9.7编写
# 使用蒙特卡罗树搜索算法来决定电脑的落子
# 使用命令行界面来交互
# 棋盘大小为11*11，用0代表空位，用1代表人类棋手，用2代表电脑棋手
# 每次输入X Y来落子，XY之间空一格，X和Y都是从0到10的整数
# 如果在水平、垂直或者对角线上连成四个自己的棋子，则输掉游戏

import random
import math

# 定义棋盘类
class Board:
    # 初始化棋盘
    def __init__(self):
        self.size = 11 # 棋盘大小
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)] # 棋盘矩阵
        self.winner = None # 胜者，None表示还没有胜者

    # 打印棋盘
    def print(self):
        print("  ", end="")
        for i in range(self.size):
            print(i, end=" ")
        print()
        for i in range(self.size):
            print(i, end=" ")
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    print(".", end=" ")
                elif self.grid[i][j] == 1:
                    print("X", end=" ")
                elif self.grid[i][j] == 2:
                    print("O", end=" ")
            print()

    # 判断是否有四连珠，如果有则返回输掉的玩家，如果没有则返回None
    def check_four(self):
        # 检查水平方向
        for i in range(self.size):
            for j in range(self.size - 3):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i][j+1] == self.grid[i][j+2] == self.grid[i][j+3]:
                    return self.grid[i][j]
        # 检查垂直方向
        for i in range(self.size - 3):
            for j in range(self.size):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i+1][j] == self.grid[i+2][j] == self.grid[i+3][j]:
                    return self.grid[i][j]
        # 检查正对角线方向
        for i in range(self.size - 3):
            for j in range(self.size - 3):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i+1][j+1] == self.grid[i+2][j+2] == self.grid[i+3][j+3]:
                    return self.grid[i][j]
        # 检查反对角线方向
        for i in range(3, self.size):
            for j in range(self.size - 3):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i-1][j+1] == self.grid[i-2][j+2] == self.grid[i-3][j+3]:
                    return self.grid[i][j]
        # 如果都没有四连珠，则返回None
        return None

    # 判断棋盘是否已满，如果已满则返回True，如果还有空位则返回False
    def is_full(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return False
        return True

    # 落子，如果成功则返回True，如果失败则返回False
    def move(self, x, y, player):
        # 判断坐标是否合法
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        # 判断位置是否为空
        if self.grid[x][y] != 0:
            return False
        # 落子
        self.grid[x][y] = player
        # 判断是否有四连珠，如果有则更新胜者
        self.winner = self.check_four()
        # 返回成功
        return True

    # 撤销落子，如果成功则返回True，如果失败则返回False
    def undo(self, x, y):
        # 判断坐标是否合法
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        # 判断位置是否非空
        if self.grid[x][y] == 0:
            return False
        # 撤销落子
        self.grid[x][y] = 0
        # 更新胜者为None
        self.winner = None
        # 返回成功
        return True

    # 复制棋盘，返回一个新的棋盘对象
    def copy(self):
        new_board = Board()
        for i in range(self.size):
            for j in range(self.size):
                new_board.grid[i][j] = self.grid[i][j]
        new_board.winner = self.winner
        return new_board

# 定义蒙特卡罗树搜索节点类
class Node:
    # 初始化节点
    def __init__(self, board, parent, move):
        self.board = board # 节点对应的棋盘状态
        self.parent = parent # 父节点
        self.move = move # 从父节点到当前节点的落子位置，用(x,y)表示，如果是根节点则为None
        self.children = [] # 子节点列表
        self.visits = 0 # 访问次数
        self.wins = 0 # 获胜次数

    # 扩展子节点，返回一个新的子节点对象，如果没有可扩展的子节点则返回None
    def expand(self):
        moves = [] # 可扩展的落子位置列表
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.grid[i][j] == 0: # 如果位置为空，则可以扩展
                    moves.append((i,j))
        if len(moves) == 0: # 如果没有可扩展的落子位置，则返回None
            return None
        move = random.choice(moves) # 随机选择一个落子位置
        new_board = self.board.copy() # 复制当前棋盘状态
        # 根据当前节点是谁的回合来决定落子的玩家，1表示人类，2表示电脑
        player = 2 if len(self.children) % 2 == 0 else 1
        # 在新的棋盘上落子
        new_board.move(move[0], move[1], player)
        # 创建一个新的子节点
        new_node = Node(new_board, self, move)
        # 将新的子节点加入到当前节点的子节点列表中
        self.children.append(new_node)
        # 返回新的子节点
        return new_node

    # 模拟随机对局，返回输掉的玩家，如果平局则返回0
    def simulate(self):
        # 复制当前棋盘状态
        board = self.board.copy()
        # 根据当前节点是谁的回合来决定下一个落子的玩家，1表示人类，2表示电脑
        player = 1 if len(self.children) % 2 == 0 else 2
        # 循环直到游戏结束
        while True:
            # 如果棋盘已满，则平局，返回0
            if board.is_full():
                return 0
            # 随机选择一个空位落子
            moves = [] # 空位列表
            for i in range(board.size):
                for j in range(board.size):
                    if board.grid[i][j] == 0: # 如果位置为空，则加入列表
                        moves.append((i,j))
            move = random.choice(moves) # 随机选择一个空位
            board.move(move[0], move[1], player) # 落子
            # 如果有四连珠，则游戏结束，返回输掉的玩家
            loser = board.check_four()
            if loser is not None:
                return loser
            # 切换玩家
            player = 1 if player == 2 else 2

    # 回溯更新访问次数和获胜次数，如果当前节点是输掉的玩家的回合，则增加获胜次数，否则不变
    def backpropagate(self, loser):
        # 更新当前节点的访问次数
        self.visits += 1
        # 根据当前节点是谁的回合来决定是否增加获胜次数，1表示人类，2表示电脑
        player = 2 if len(self.children) % 2 == 0 else 1
        if player != loser: # 如果当前节点不是输掉的玩家的回合，则增加获胜次数
            self.wins += 1
        # 如果有父节点，则递归回溯更新父节点
        if self.parent is not None:
            self.parent.backpropagate(loser)

    # 判断节点对应的棋盘是否已满，如果已满则返回True，如果还有空位则返回False
    def is_full(self):
        return self.board.is_full()

# 定义蒙特卡罗树搜索类
class MCTS:
    # 初始化搜索树，传入初始棋盘状态和搜索时间限制（秒）
    def __init__(self, board, time_limit):
        self.root = Node(board, None, None) # 根节点
        self.time_limit = time_limit # 时间限制

    # 搜索最佳落子位置，返回一个(x,y)元组，如果没有可行的落子位置则返回None
    def search(self):
        import time
        start_time = time.time() # 记录开始时间
        while time.time() - start_time < self.time_limit: # 循环直到超过时间限制
            node = self.root # 从根节点开始选择节点
            while True: # 循环直到找到一个可扩展或者可模拟的节点为止
                if node.board.winner is not None: # 如果当前节点对应的棋盘状态
                # 已经有胜者，则无法扩展或者模拟，直接回溯更新
                    node.backpropagate(node.board.winner)
                    break
                elif node.is_full(): # 如果当前节点对应的棋盘状态已满，则平局，也无法扩展或者模拟，直接回溯更新
                    node.backpropagate(0)
                    break
                elif len(node.children) == 0: # 如果当前节点没有子节点，则尝试扩展一个子节点
                    new_node = node.expand()
                    if new_node is None: # 如果无法扩展，则平局，回溯更新
                        node.backpropagate(0)
                        break
                    else: # 如果成功扩展，则模拟随机对局，回溯更新
                        loser = new_node.simulate()
                        new_node.backpropagate(loser)
                        break
                else: # 如果当前节点有子节点，则根据UCB1公式选择一个最优的子节点继续选择
                    best_score = -1 # 最优的分数
                    best_child = None # 最优的子节点
                    for child in node.children: # 遍历所有子节点
                        # 计算UCB1分数，其中C为常数，这里取1.414，w为获胜次数，n为访问次数，N为父节点的访问次数
                        score = child.wins / child.visits + 1.414 * math.sqrt(math.log(node.visits) / child.visits)
                        if score > best_score: # 如果分数更高，则更新最优的分数和最优的子节点
                            best_score = score
                            best_child = child
                    node = best_child # 选择最优的子节点继续选择

        # 在时间限制内完成了若干次选择-扩展-模拟-回溯的过程后，从根节点的子节点中选择访问次数最多的子节点作为最佳落子位置
        best_move = None # 最佳落子位置
        best_visits = -1 # 最多访问次数
        for child in self.root.children: # 遍历根节点的所有子节点
            if child.visits > best_visits: # 如果访问次数更多，则更新最佳落子位置和最多访问次数
                best_move = child.move
                best_visits = child.visits
        return best_move # 返回最佳落子位置

# 定义游戏类
class Game:
    # 初始化游戏，传入搜索时间限制（秒）
    def __init__(self, time_limit):
        self.board = Board() # 棋盘对象
        self.time_limit = time_limit # 搜索时间限制

    # 开始游戏，循环直到游戏结束
    def start(self):
        print("欢迎来到反四子棋！")
        print("你是X，电脑是O。")
        print("每次输入X Y来落子，XY之间空一格，X和Y都是从0到10的整数。")
        print("如果在水平、垂直或者对角线上连成四个自己的棋子，则输掉游戏。")
        print("祝你好运！")
        self.board.print() # 打印初始棋盘

        while True: # 循环直到游戏结束

            # 人类回合
            while True: # 循环直到输入合法的落子位置为止
                try: # 尝试获取输入并转换为整数坐标
                    x, y = map(int, input("请输入你的落子位置：").split())
                except ValueError: # 如果输入不合法，则```
                    print("输入不合法，请重新输入。")
                    continue
                if self.board.move(x, y, 1): # 如果落子成功，则跳出循环
                    break
                else: # 如果落子失败，则提示并继续循环
                    print("落子位置不合法，请重新输入。")

            self.board.print() # 打印棋盘

            # 判断是否有胜者，如果有则结束游戏
            if self.board.winner is not None:
                if self.board.winner == 1:
                    print("你输了！")
                elif self.board.winner == 2:
                    print("你赢了！")
                break

            # 判断是否平局，如果是则结束游戏
            if self.board.is_full():
                print("平局！")
                break

            # 电脑回合
            print("电脑正在思考中...")
            mcts = MCTS(self.board, self.time_limit) # 创建蒙特卡罗树搜索对象
            x, y = mcts.search() # 搜索最佳落子位置
            self.board.move(x, y, 2) # 落子
            print(f"电脑落子在{x} {y}")
            self.board.print() # 打印棋盘

            # 判断是否有胜者，如果有则结束游戏
            if self.board.winner is not None:
                if self.board.winner == 1:
                    print("你输了！")
                elif self.board.winner == 2:
                    print("你赢了！")
                break

            # 判断是否平局，如果是则结束游戏
            if self.board.is_full():
                print("平局！")
                break

# 创建游戏对象，设置搜索时间限制为5秒
game = Game(5)
# 开始游戏
game.start()
