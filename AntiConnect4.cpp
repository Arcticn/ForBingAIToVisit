#include <iostream>
#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <ctime>
#include <cstdlib>
#include <unordered_map>
#include "jsoncpp/json.h"
using namespace std;

// 定义棋盘大小
const int BOARD_SIZE = 11;

// 定义评估函数的权重
const int WIN_SCORE = 1000000;
const int LOSE_SCORE = -1000000;
const int INF = 1000000000;
const int PENALTY = 10;

// 定义模拟的时间限制
const int TIME_LIMIT_MS = 980;
// 定义模拟的初始深度
int INIT_DEPTH = 4;

int SIM_MOVE_CNT = 10;

// 定义棋盘状态，0表示空位，1表示计算机棋手，-1表示人类棋手
vector<vector<int>> board(BOARD_SIZE, vector<int>(BOARD_SIZE, 0));

// 定义当前轮到哪一方下棋，1表示计算机棋手，-1表示人类棋手

struct pair_hash {
    template <class T1, class T2>
    std::size_t operator() (const std::pair<T1, T2>& p) const {
        auto h1 = std::hash<T1>{}(p.first);
        auto h2 = std::hash<T2>{}(p.second);
        return h1 ^ h2;
    }
};

// 定义一个函数来计算评估函数，返回当前棋盘状态对计算机棋手的分数
int evaluate(int x, int y, int turn, int normal) {
    int score = 0; // 初始化分数为0
    if ((x == 0 && y == 0) || (x == 0 && y == BOARD_SIZE - 1) || (x == BOARD_SIZE - 1 && y == 0) || (x == BOARD_SIZE - 1 && y == BOARD_SIZE - 1)) {
        score += 15000;
    }
    if ((x == 0 && y == 1) || (x == 1 && y == 0) || (x == BOARD_SIZE - 2 && y == 0) || (x == BOARD_SIZE - 1 && y == 1) || (x == 0 && y == BOARD_SIZE - 2) || (x == 1 && y == BOARD_SIZE - 1) || (x == BOARD_SIZE - 2 && y == BOARD_SIZE - 1) || (x == BOARD_SIZE - 1 && y == BOARD_SIZE - 2)) {
        score += 10000;
    }
    if (x == 0 || x == BOARD_SIZE - 1 || y == 0 || y == BOARD_SIZE - 1) {
        score += 2000;
    }
    else if (x == 1 || x == BOARD_SIZE - 2 || y == 1 || y == BOARD_SIZE - 2) {
        score += 1100;
    }

    int dx[4] = { 1, 0, 1, 1 };
    int dy[4] = { 0, 1, 1, -1 };

    for (int k = 0; k < 4; k++) {
        int count = 1;
        int space_count = 0;
        int max_count = 1;
        int sign = 1;
        for (int i = 1; i < 4; i++) {
            int cur_x = x + dx[k] * i;
            int cur_y = y + dy[k] * i;
            if (cur_x >= 0 && cur_x < BOARD_SIZE && cur_y >= 0 && cur_y < BOARD_SIZE) {
                if (board[cur_x][cur_y] == turn) {
                    count += 1;
                    if (sign == 1) {
                        max_count += 1;
                    }
                }
                else if (board[cur_x][cur_y] == 0) {
                    space_count += 1;
                    sign = 0;
                }
                else {
                    break;
                }
            }
        }

        sign = 1;
        for (int i = -1; i > -4; i--) {
            int cur_x = x + dx[k] * i;
            int cur_y = y + dy[k] * i;
            if (cur_x >= 0 && cur_x < BOARD_SIZE && cur_y >= 0 && cur_y < BOARD_SIZE) {
                if (board[cur_x][cur_y] == turn) {
                    count += 1;
                    if (sign == 1) {
                        max_count += 1;
                    }
                }
                else if (board[cur_x][cur_y] == 0) {
                    space_count += 1;
                    sign = 0;
                }
                else {
                    break;
                }
            }
        }

        if (max_count >= 4)
            score += LOSE_SCORE;
        if (count + space_count <= 3)   //XOOOX XOOX XOX
            score += 800;

        int cur_x_1 = x + dx[k] * 1;
        int cur_y_1 = y + dy[k] * 1;
        int cur_x_2 = x + dx[k] * 2;
        int cur_y_2 = y + dy[k] * 2;
        int cur_x_3 = x + dx[k] * 3;
        int cur_y_3 = y + dy[k] * 3;
        int cur_x_r1 = x + dx[k] * -1;
        int cur_y_r1 = y + dy[k] * -1;
        int cur_x_r2 = x + dx[k] * -2;
        int cur_y_r2 = y + dy[k] * -2;
        int cur_x_r3 = x + dx[k] * -3;
        int cur_y_r3 = y + dy[k] * -3;

        // .1 ? ? ?
        if (cur_x_3 >= 0 && cur_x_3 < BOARD_SIZE && cur_y_3 >= 0 && cur_y_3 < BOARD_SIZE) {
            if (board[cur_x_1][cur_y_1] == 0 && board[cur_x_2][cur_y_2] == turn && board[cur_x_3][cur_y_3] == turn) {
                score -= 10000; // .1 0 1 1
            }
            if (board[cur_x_1][cur_y_1] == turn && board[cur_x_2][cur_y_2] == 0 && board[cur_x_3][cur_y_3] == turn) {
                score -= 10000; // .1 1 0 1
            }
            if (board[cur_x_1][cur_y_1] == turn && board[cur_x_2][cur_y_2] == turn && board[cur_x_3][cur_y_3] == 0) {
                score -= 10000; // .1 1 1 0
            }
        }

        // ? .1 ? ?
        if (cur_x_r1 >= 0 && cur_x_r1 < BOARD_SIZE && cur_y_r1 >= 0 && cur_y_r1 < BOARD_SIZE && cur_x_2 >= 0 && cur_x_2 < BOARD_SIZE && cur_y_2 >= 0 && cur_y_2 < BOARD_SIZE) {
            if (board[cur_x_r1][cur_y_r1] == turn && board[cur_x_2][cur_y_2] == turn && board[cur_x_1][cur_y_1] == 0) {
                score -= 10000; // 1 .1 0 1
            }
            if (board[cur_x_r1][cur_y_r1] == turn && board[cur_x_1][cur_y_1] == turn && board[cur_x_2][cur_y_2] == 0) {
                score -= 10000; // 1 .1 1 0
            }
            if (board[cur_x_r1][cur_y_r1] == 0 && board[cur_x_1][cur_y_1] == turn && board[cur_x_2][cur_y_2] == turn) {
                score -= 10000; // 0 .1 1 1
            }
        }
        // ? ? .1 ?
        if (cur_x_r2 >= 0 && cur_x_r2 < BOARD_SIZE && cur_y_r2 >= 0 && cur_y_r2 < BOARD_SIZE &&
            cur_x_1 >= 0 && cur_x_1 < BOARD_SIZE && cur_y_1 >= 0 && cur_y_1 < BOARD_SIZE) {
            if (board[cur_x_r2][cur_y_r2] == turn && board[cur_x_r1][cur_y_r1] == 0 && board[cur_x_1][cur_y_1] == turn) {
                score -= 10000; // 1 0 .1 1
            }
            if (board[cur_x_r2][cur_y_r2] == turn && board[cur_x_r1][cur_y_r1] == turn && board[cur_x_1][cur_y_1] == 0) {
                score -= 10000; // 1 1 .1 0
            }
            if (board[cur_x_r2][cur_y_r2] == 0 && board[cur_x_r1][cur_y_r1] == turn && board[cur_x_1][cur_y_1] == turn) {
                score -= 10000; // 0 1 .1 1
            }
        }

        // ? ? ? .1
        if (cur_x_r3 >= 0 && cur_x_r3 < BOARD_SIZE && cur_y_r3 >= 0 && cur_y_r3 < BOARD_SIZE) {
            if (board[cur_x_r3][cur_y_r3] == turn && board[cur_x_r2][cur_y_r2] == 0 && board[cur_x_r1][cur_y_r1] == turn) {
                score -= 10000; // 1 0 1 .1
            }
            if (board[cur_x_r3][cur_y_r3] == turn && board[cur_x_r2][cur_y_r2] == turn && board[cur_x_r1][cur_y_r1] == 0) {
                score -= 10000; // 1 1 0 .1
            }
            if (board[cur_x_r3][cur_y_r3] == 0 && board[cur_x_r2][cur_y_r2] == turn && board[cur_x_r1][cur_y_r1] == turn) {
                score -= 10000; // 0 1 1 .1
            }
        }
    }

    if (normal == 1) {
        turn = -turn;
        board[x][y] = turn;
        score += evaluate(x, y, turn, 0);
        turn = -turn;
        board[x][y] = turn;
    }

    return score;
}

// 定义一个函数来判断是否连成四个或以上的棋子，返回True或False
bool is_win(int x, int y) {
    // 获取当前位置的棋子
    int piece = board[x][y];
    // 初始化连续棋子数为1
    int count = 1;
    // 检查水平方向左边
    int i = x - 1;
    while (i >= 0 && board[i][y] == piece) {
        count += 1;
        i -= 1;
    }
    // 检查水平方向右边
    i = x + 1;
    while (i < BOARD_SIZE && board[i][y] == piece) {
        count += 1;
        i += 1;
    }
    // 如果连续棋子数大于等于4，返回True
    if (count >= 4) {
        return true;
    }

    // 初始化连续棋子数为1
    count = 1;
    // 检查垂直方向上边
    int j = y - 1;
    while (j >= 0 && board[x][j] == piece) {
        count += 1;
        j -= 1;
    }
    // 检查垂直方向下边
    j = y + 1;
    while (j < BOARD_SIZE && board[x][j] == piece) {
        count += 1;
        j += 1;
    }
    // 如果连续棋子数大于等于4，返回True
    if (count >= 4) {
        return true;
    }

    // 初始化连续棋子数为1
    count = 1;
    // 检查正对角线方向左上
    i = x - 1;
    j = y - 1;
    while (i >= 0 && j >= 0 && board[i][j] == piece) {
        count += 1;
        i -= 1;
        j -= 1;
    }
    // 检查正对角线方向右下
    i = x + 1;
    j = y + 1;
    while (i < BOARD_SIZE && j < BOARD_SIZE && board[i][j] == piece) {
        count += 1;
        i += 1;
        j += 1;
    }
    // 如果连续棋子数大于等于4，返回true
    if (count >= 4) {
        return true;
    }

    // 初始化连续棋子数为1
    count = 1;
    // 检查反对角线方向左下
    i = x - 1;
    j = y + 1;
    while (i >= 0 && j < BOARD_SIZE && board[i][j] == piece) {
        count += 1;
        i -= 1;
        j += 1;
    }
    // 检查反对角线方向右上
    i = x + 1;
    j = y - 1;
    while (i < BOARD_SIZE && j >= 0 && board[i][j] == piece) {
        count += 1;
        i += 1;
        j -= 1;
    }
    // 如果连续棋子数大于等于4，返回true
    if (count >= 4) {
        return true;
    }
    // 棋子未连成四个或以上，返回False
    return false;
}

// 定义一个函数来生成可落子位置，返回一个列表，每个元素是一个坐标元组(x, y)
vector<pair<int, int>> generate_moves() {
    vector<pair<int, int>> moves; // 初始化可落子位置为空列表
    // 遍历所有的空位，如果落子后不会导致自己连成四个或以上的棋子，就加入可落子位置列表中
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == 0) { // 如果是空位
                board[i][j] = 1; // 尝试落子
                if (!is_win(i, j)) { // 如果不会导致自己连成四个或以上的棋子
                    moves.push_back(make_pair(i, j)); // 加入可落子位置列表中
                }
                board[i][j] = 0; // 恢复空位
            }
        }
    }
    // 返回可落子位置列表
    // random_shuffle(moves.begin(), moves.end());
    return moves;
}

pair<int, int> simulate(int depth, double start_time, int turn, vector<pair<int, int>> moves) {
    // 如果没有可落子位置，或者已经达到模拟的深度，或者已经超过模拟的时间限制，就返回当前的分数和None
    if (moves.empty() || depth == 0) {
        return { 0, 0 };
    }

    if ((clock() - start_time) * 1000.0 / CLOCKS_PER_SEC > TIME_LIMIT_MS) {
        return { 0, 1 };
    }

    // 初始化最佳的分数和最佳的落子位置为None
    unordered_map<pair<int, int>, int, pair_hash> scores;

    int sign = 0; //定义是否是超时退出的
    for (auto& move : moves) {
        // 获取坐标
        int x = move.first;
        int y = move.second;
        // 落子
        board[x][y] = turn;
        // 计算当前的分数
        int score = evaluate(x, y, turn, 1);
        // 恢复空位
        board[x][y] = 0;
        // 将最佳的分数累加到对应的可落子位置的分数上
        scores[move] = score;
    }

    // 对可落子位置按照分数降序排序，选择分数最高的落子位置作为最优解
    sort(moves.begin(), moves.end(), [&](const pair<int, int>& a, const pair<int, int>& b) {
        return scores[a] > scores[b];
        });

    int cnt = SIM_MOVE_CNT;
    if (moves.size() < cnt)cnt = moves.size();
    vector<pair<int, int>> top_moves(moves.begin(), moves.begin() + cnt);

    for (auto& move : top_moves) {
        // 获取坐标
        int x = move.first;
        int y = move.second;
        if (sign == 0) {
            // 落子
            board[x][y] = turn;
            // 切换轮次
            turn = -turn;

            vector<pair<int, int>> smoves = moves;
            smoves.erase(remove(smoves.begin(), smoves.end(), move), smoves.end());
            // 模拟回溯，获取最佳的分数
            auto [best_score, sub_sign] = simulate(depth - 1, start_time, turn, smoves);
            sign = sub_sign;
            // 恢复轮次
            turn = -turn;
            // 恢复空位
            board[x][y] = 0;
            // 将最佳的分数累加到对应的可落子位置的分数上
            if (sign == 0) {
                scores[move] -= best_score;
            }
            else {
                scores[move] = -INF;
            }
        }
        else {
            scores[move] = -INF;
        }
    }

    sort(top_moves.begin(), top_moves.end(), [&](const pair<int, int>& a, const pair<int, int>& b) {
        return scores[a] > scores[b];
        });

    int best_score1 = scores[top_moves[0]];

    // 返回最佳的分数和最佳的落子位置
    return { best_score1, sign };
}

tuple<pair<int, int>, int, double, int> choose_best_move() {
    // 获取可落子位置列表
    vector<pair<int, int>> moves = generate_moves();
    // 初始化开始时间为当前时间
    std::clock_t start_time = std::clock(); // 记录开始时间
    // 如果没有可落子位置，就返回None
    if (moves.empty()) {
        return make_tuple(make_pair(-1, -1), -1, 0, 0);
    }
    // 初始化最优解为None
    pair<int, int> best_move = make_pair(-1, -1);
    // 初始化遍历完成的点的个数为0
    int visited = 0;
    // 初始化模拟的深度为初始深度
    int depth = INIT_DEPTH;
    int sign = 0;

    int turn = 1;
    // 初始化一个字典来存储每个可落子位置的分数，初始值为0
    unordered_map<pair<int, int>, int, pair_hash> scores;
    for (const auto& move : moves) {
        int x = move.first, y = move.second;
        board[x][y] = turn;
        // 计算当前的分数
        int score = evaluate(x, y, turn, 1);
        // 恢复空位
        board[x][y] = 0;
        // 将最佳的分数累加到对应的可落子位置的分数上
        scores[move] = score;
    }

    // 对可落子位置按照分数降序排序，选择分数最高的落子位置作为最优解
    sort(moves.begin(), moves.end(), [&](const pair<int, int>& a, const pair<int, int>& b) {
        return scores[a] > scores[b];
        });
    int cnt = 50;
    if (moves.size() < cnt)cnt = moves.size();
    vector<pair<int, int>> top_moves(moves.begin(), moves.begin() + cnt);
    for (const auto& move : top_moves) {
        int x = move.first, y = move.second;
        if (sign == 0) {
            board[x][y] = turn;
            turn = -turn;
            vector<pair<int, int>> smoves(moves);
            smoves.erase(find(smoves.begin(), smoves.end(), move));
            auto [best_score, sub_sign] = simulate(depth, start_time, turn, smoves);
            turn = -turn;
            board[x][y] = 0;
            sign = sub_sign;
            if (sign == 0) {
                scores[move] -= best_score;
                visited++;
            }
            else {
                scores[move] = -INF;
            }
        }
        else {
            scores[move] = -INF;
        }
    }
    sort(top_moves.begin(), top_moves.end(), [&](const pair<int, int>& a, const pair<int, int>& b) {
        return scores[a] > scores[b];
        });
    best_move = top_moves[0];

    std::clock_t end_time = std::clock(); // 记录结束时间
    double duration = (end_time - start_time) / static_cast<double>(CLOCKS_PER_SEC); // 计算时间差
    // 返回最优解
    return make_tuple(best_move, depth, duration, visited);
}

int main()
{
    // 读入JSON
    string str;
    getline(cin, str);
    Json::Reader reader;
    Json::Value input;
    reader.parse(str, input);

    // 分析自己收到的输入和自己过往的输出，并恢复状态

    int turnID = input["responses"].size();
    for (int i = 0; i < turnID; i++)
    {
        auto& myInput = input["requests"][i];
        auto& myOutput = input["responses"][i];
        if (myInput["x"] >= 0) { // 如果人类棋手有落子，就更新棋盘状态和轮次
            board[myInput["x"].asInt()][myInput["y"].asInt()] = -1;
        }
        if (myOutput["x"] >= 0) { // 如果计算机棋手有落子，就更新棋盘状态和轮次
            board[myOutput["x"].asInt()][myOutput["y"].asInt()] = 1;
        }
    }

    auto& myInput = input["requests"][turnID];
    if (myInput["x"] >= 0) { // 如果人类棋手有落子，就更新棋盘状态和轮次
        board[myInput["x"].asInt()][myInput["y"].asInt()] = -1;
    }

    if (input.isMember("data")) {
        auto& myData = input["data"];
        INIT_DEPTH = myData["depth"].asInt();
    }

    if (turnID >= 35)SIM_MOVE_CNT = 12;
    if (turnID >= 45) {
        SIM_MOVE_CNT = 15;
    }
    // 选择最优解
    auto [best_move, depth, Ftime, Fvisit] = choose_best_move();

    // 输出落子位置
    if (best_move.first != -1 && best_move.second != -1)
    {
        Json::Value response;
        response["x"] = best_move.first;
        response["y"] = best_move.second;

        Json::Value data;
        data["depth"] = INIT_DEPTH;

        Json::Value debug;
        debug["depth"] = INIT_DEPTH;
        debug["time"] = Ftime; // 填上计算时间
        debug["visit"] = Fvisit; // 填上节点数

        Json::Value output;
        output["response"] = response;
        output["data"] = data;
        output["debug"] = debug;

        Json::FastWriter writer;
        cout << writer.write(output) << endl;
    }
    else
    {
        Json::Value response;
        response["x"] = -1;
        response["y"] = -1;

        Json::Value output;
        output["response"] = response;

        Json::FastWriter writer;
        cout << writer.write(output) << endl;
    }
}

