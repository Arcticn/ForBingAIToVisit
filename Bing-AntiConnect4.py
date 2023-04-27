# 导入json模块
import json
# 导入time模块
import time
# 定义棋盘大小
BOARD_SIZE = 11
# 定义棋子颜色
BLACK = 1
WHITE = -1
EMPTY = 0
# 定义无穷大和无穷小
INF = float("inf")
NINF = float("-inf")
# 定义时间限制
TIME_LIMIT = 5.5

# 定义一个棋盘类
class Board:
    # 初始化棋盘状态和回合数
    def __init__(self):
        self.state = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = BLACK

    # 根据输入的棋步更新棋盘状态和回合数
    def update(self, x, y):
        self.state[x][y] = self.turn
        self.turn = -self.turn

    # 判断一个位置是否在棋盘范围内
    def in_range(self, x, y):
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    # 判断一个位置是否为空
    def is_empty(self, x, y):
        return self.state[x][y] == EMPTY

    # 判断一个位置是否是己方的禁入点（连成四个或以上的棋子）
    def is_self_forbidden(self, x, y):
        return self.count(x, y, self.turn) >= 4

    # 判断一个位置是否是对方的禁入点（连成四个或以上的棋子）
    def is_oppo_forbidden(self, x, y):
        return self.count(x, y, -self.turn) >= 4

    # 判断一个位置是否是无影响点（完全不产生任何影响）
    def is_no_effect(self, x, y):
        return self.count(x, y, self.turn) == 0 and self.count(x, y, -self.turn) == 0

    # 统计一个位置在四个方向上的连子数（水平，垂直，对角线，反对角线）
    def count(self, x, y, color):
        max_count = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 1
            i = x + dx
            j = y + dy
            while self.in_range(i, j) and self.state[i][j] == color:
                count += 1
                i += dx
                j += dy
            i = x - dx
            j = y - dy
            while self.in_range(i, j) and self.state[i][j] == color:
                count += 1
                i -= dx
                j -= dy
            max_count = max(max_count, count)
        return max_count

    # 计算一个位置的启发式评分（根据用户的理解）
    def evaluate(self, x, y):
        score = 0
        # 角上和边上的棋子有优势，给予正分（越靠外越好）
        score += min(x + 1, BOARD_SIZE - x) + min(y + 1, BOARD_SIZE - y)
        # 中心区域的棋子有更多的可能性，给予正分（越靠近中心越好）
        score += abs(x - BOARD_SIZE // 2) + abs(y - BOARD_SIZE // 2)
        # 己方连成三个一线的棋子可以让对方陷入两难，给予正分（越多越好）
        if self.count(x, y, self.turn) == 3:
            score += 10
        # 己方连成四个或以上的棋子会导致失败，给予负分（越多越坏）
        if self.count(x, y, self.turn) >= 4:
            score -= 100
        # 对方连成三个一线的棋子也可以让自己陷入两难，给予负分（越多越坏）
        if self.count(x, y, -self.turn) == 3:
            score -= 10
        # 对方连成四个或以上的棋子会导致胜利，给予正分（越多越好）
        if self.count(x, y, -self.turn) >= 4:
            score += 100
        return score
    
# 定义一个minimax类
class Minimax:
    # 初始化棋盘，深度，时间和模仿棋的标志
    def __init__(self, board, depth, time_limit, imitation):
        self.board = board
        self.depth = depth
        self.time_limit = time_limit
        self.imitation = imitation
        self.start_time = None

    # 判断是否超时
    def is_timeout(self):
        return time.time() - self.start_time > self.time_limit

    # 判断是否游戏结束（有一方连成四个或以上的棋子）
    def is_game_over(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board.count(i, j, BLACK) >= 4 or self.board.count(i, j, WHITE) >= 4:
                    return True
        return False

    # 生成所有可能的落子位置（空位且不是己方或对方的禁入点）
    def generate_moves(self):
        moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board.is_empty(i, j) and not (self.board.is_self_forbidden(i, j) or self.board.is_oppo_forbidden(i, j)):
                    moves.append((i, j))
        return moves

    # 实现minimax算法和alpha-beta剪枝，返回最佳的落子位置和评分
    def minimax(self):
        # 记录开始时间
        self.start_time = time.time()
        # 如果是先手且是第一回合，就下在中心位置（最优策略）
        if self.board.turn == BLACK and len(self.board.state) == 0:
            return (BOARD_SIZE // 2, BOARD_SIZE // 2), INF
        # 如果是后手且是第二回合，就模仿对方的落子（最优策略）
        if self.board.turn == WHITE and len(self.board.state) == 1 and self.imitation:
            x, y = self.board.state[0]
            return (BOARD_SIZE - x - 1, BOARD_SIZE - y - 1), INF
        # 否则，调用max_value函数，寻找最大化自己的评分的落子位置
        best_move = None
        best_score = NINF
        alpha = NINF
        beta = INF
        for move in self.generate_moves():
            x, y = move
            self.board.update(x, y)
            score = self.min_value(self.depth - 1, alpha, beta)
            self.board.update(x, y)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_move, best_score

    # 定义max_value函数，返回最大化自己的评分的值（用于电脑的回合）
    def max_value(self, depth, alpha, beta):
        # 如果超时或者游戏结束或者达到最大深度，就返回当前棋盘状态的评分（用启发式函数）
        if self.is_timeout() or self.is_game_over() or depth == 0:
            return self.evaluate()
        # 否则，遍历所有可能的落子位置，寻找最大化自己的评分的值
        value = NINF
        for move in self.generate_moves():
            x, y = move
            self.board.update(x, y)
            value = max(value, self.min_value(depth - 1, alpha, beta))
            self.board.update(x, y)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    # 定义min_value函数，返回最小化对方的评分的值（用于对方的回合）
    def min_value(self, depth, alpha, beta):
        # 如果超时或者游戏结束或者达到最大深度，就返回当前棋盘状态的评分（用启发式函数）
        if self.is_timeout() or self.is_game_over() or depth == 0:
            return self.evaluate()
        # 否则，遍历所有可能的落子位置，寻找最小化对方的评分的值
        value = INF
        for move in self.generate_moves():
            x, y = move
            self.board.update(x, y)
            value = min(value, self.max_value(depth - 1, alpha, beta))
            self.board.update(x, y)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value
    
    # 定义启发式函数，用于评估当前棋盘状态的价值（根据用户的理解）
    def evaluate(self):
        score = 0
        # 遍历所有的位置
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                # 如果是空位，就计算该位置的评分，并根据回合数加权（越靠后越重要）
                if self.board.is_empty(i, j):
                    score += self.board.evaluate(i, j) * (1 + len(self.board.state) / (BOARD_SIZE ** 2))
        return score
    
# 定义主函数
def main():
    # 读取输入
    full_input = json.loads(input())
    all_requests = full_input["requests"]
    all_responses = full_input["responses"]
    # 创建一个棋盘对象
    board = Board()
    # 根据历史棋步还原棋盘状态和回合数（注意requests的数量比responses多一个）
    for i in range(len(all_responses)):
        myInput = all_requests[i]
        myOutput = all_responses[i]
        if myInput["x"] >= 0:
            board.update(myInput["x"], myInput["y"])
        if myOutput["x"] >= 0:
            board.update(myOutput["x"], myOutput["y"])
    # 更新最后一个request
    myInput = all_requests[-1]
    if myInput["x"] >= 0:
        board.update(myInput["x"], myInput["y"])
    # 创建一个minimax对象，设置深度为3，时间限制为5.5秒，模仿棋为True
    minimax = Minimax(board, 3, 5.5, True)
    # 尝试调用minimax算法，得到最佳的落子位置和评分
    best_move, best_score = minimax.minimax()
    # 如果出现异常，就寻找对手的禁入点，如果没有，就随机选择一个空位
    if best_move is None:
        best_move = minimax.find_oppo_forbidden()
        if best_move is None:
            best_move = minimax.random_empty()
    # 输出结果
    print(json.dumps({"response": {"x": best_move[0], "y": best_move[1]}}))

# 调用主函数
if __name__ == "__main__":
    main()
