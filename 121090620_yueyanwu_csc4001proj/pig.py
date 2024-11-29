

def eval_expr(expr, vars):
    expr = expr.replace(" ", "")  # 清除空格
    # print(expr)
    postfix_expr = infix_to_postfix(expr, vars)  # 将中缀表达式转换为后缀表达式
    # print("post",postfix_expr)
    return calculate_postfix(postfix_expr, vars)  # 计算后缀表达式

def infix_to_postfix(expr, vars):
    precedence = {'!': 3, '&': 2, '|': 2, '+': 1, '-': 1}
    stack = []
    output = []
    i = 0
    while i < len(expr):
        if expr[i].isdigit() or (expr[i] == '!' and expr[i + 1].isdigit()):
            # 处理数字，包括正负数
            num = ''
            if expr[i] == '!':
                num += expr[i]
                i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            output.append(num)
            continue
        if expr[i].isalpha():
            # 处理变量名
            var_name = ''
            while i < len(expr) and expr[i].isalnum():
                var_name += expr[i]
                i += 1
            output.append(vars.get(var_name, '0' * len(next(iter(vars.values())))))  # 使用默认长度
            continue
        if expr[i] in precedence:
            # 处理运算符
            while (stack and stack[-1] != '(' and
                   precedence[stack[-1]] >= precedence[expr[i]]):
                output.append(stack.pop())
            stack.append(expr[i])
        elif expr[i] == '(':
            stack.append(expr[i])
        elif expr[i] == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # 弹出 '('
        i += 1
    while stack:
        output.append(stack.pop())
    return output

def calculate_postfix(postfix_expr, vars):
    stack = []
    for token in postfix_expr:
        if token.isdigit() or (token[0] == '!' and token[1:].isdigit()):
            # 直接推入栈，如果是数字，直接转为二进制，如果是带!的数字，计算其NOT
            if token[0] == '!':
                num = bin(~int(token[1:], 2) & (2 ** len(token[1:]) - 1))[2:].zfill(len(token[1:]))
                stack.append(num)
            else:
                stack.append(bin(int(token, 2))[2:].zfill(len(token)))
        elif token in vars:
            # 如果是变量，直接推入变量的值
            stack.append(vars[token])
        else:
            # 执行运算
            if token == '!':
                operand = stack.pop()
                result = bin(~int(operand, 2) & (2 ** len(operand) - 1))[2:].zfill(len(operand))
            else:
                right = stack.pop()
                left = stack.pop()
                if token == '+':
                    result = int(left, 2) + int(right, 2)
                elif token == '-':
                    result = int(left, 2) - int(right, 2)
                elif token == '&':
                    result = int(left, 2) & int(right, 2)
                elif token == '|':
                    result = int(left, 2) | int(right, 2)
                # 确保结果的长度与最长的操作数长度相匹配
                max_len = max(len(left), len(right))
                result = bin(result & (2 ** max_len - 1))[2:].zfill(max_len)
            stack.append(result)
    return stack.pop()


if __name__ == "__main__":
    with open("./input.pig", "r") as f:
        lines = [line.strip() for line in f]  # 一次性读取所有行并去除空格
    
    vars = {}
    var_lengths = {}
    outputs = []  # 存储输出结果，避免多次文件写操作
    current_line = 0

    max_line = len(lines)
    k = 0
    while (current_line < max_line)  & (k<5001) :
        k = k+1
        if k >=5001:
            break
        line = lines[current_line]
        
        if line.startswith('D'):
            parts = line.split()
            # vars[parts[2]] = '0' * int(parts[1][2:])  # 初始化变量为0的字符串
            # # print("vars",vars)
            var_name = parts[2]
            var_length = int(parts[1][2:])  # 从bv32这样的字符串中提取长度32
            vars[var_name] = '0' * var_length  # 初始化变量为0的字符串，长度为定义的长度
            var_lengths[var_name] = var_length  # 存储变量的长度
            # print(vars)
            

        elif line.startswith('A'):
            parts = line.split(maxsplit=2)
            # print(parts)
            var_name = parts[1]
            # print(var_name)
            expr = parts[2]
            # print("121",expr)
            result = eval_expr(expr, vars)
            # 格式化结果以匹配变量定义的长度
            if var_name in var_lengths:
                # 获取变量定义的长度
                var_length = var_lengths[var_name]
                # 将结果转换为二进制并去掉'0b'前缀，然后根据需要填充或截取
                binary_result = bin(int(result, 2))[2:].zfill(var_length)

                # 如果结果长度超过了变量的定义长度，截取最低位
                if len(binary_result) > var_length:
                    binary_result = binary_result[-var_length:]

                vars[var_name] = binary_result
            else:
                raise KeyError(f"Variable {var_name} not defined")
            # print("result ",result,)
            

        elif line.startswith('O'):
            var_name = line.split()[1]
            if var_name in vars:
                outputs.append(vars[var_name])

        elif line.startswith('B'):
            # print("come B")
            parts = line.split(maxsplit=2)
            target_line = int(parts[1])  # 行号转换为零基索引
            condition_expr = parts[2]
            # print("111",condition_expr)
            # 计算条件表达式的值
            condition_value = eval_expr(condition_expr, vars)
            # print("222",condition_value)
            # 检查条件表达式的结果是否为非零
            if int(condition_value, 2) != 0:
                # 非零表示真，执行跳转
                if 0 <= target_line < max_line:  # 确保目标行号在有效范围内
                    current_line = target_line
                else:
                    raise ValueError("Branch target line out of range.")
            else:
                # 为零表示假，执行下一行
                current_line += 1
            # print(target_line)
            continue  # 防止循环末尾再次递增 current_line



        elif line.startswith('R'):
            var_name = line.split()[1]
            vars.pop(var_name, None)  # 使用pop避免KeyError

        current_line += 1

    with open("./1.out", "w") as g:
        # g.write('\n'.join(outputs))  # 一次性将所有结果写入文件
        # if k >=5001:
        #     g.write('\ntoo-many-lines')
        # g.write('\n')
        for i in outputs:
            g.write( i+'\n')
        if k>= 5001:
            g.write('too-many-lines\n' )
