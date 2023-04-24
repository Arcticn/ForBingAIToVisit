import json

# 解析读入的JSON
full_input = json.loads(input())
if "data" in full_input:
    my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
else:
    my_data = None

# 分析自己收到的输入和自己过往的输出，并恢复状态
all_requests = full_input["requests"]
all_responses = full_input["responses"]
for i in range(len(all_responses)):
    myInput = all_requests[i] # i回合我的输入
    myOutput = all_responses[i] # i回合我的输出
    # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
    pass

# 看看自己最新一回合输入
curr_input = all_requests[-1]

# TODO: 作出决策并输出
my_action = { "x": 1, "y": 1 }

print(json.dumps({
    "response": my_action,
    "data": my_data # 可以存储一些前述的信息，在该对局下回合中使用，可以是dict或者字符串
}))
