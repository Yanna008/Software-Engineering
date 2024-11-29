# import random

# if __name__ == "__main__":
#     f = open("./input1.pig", "w")
#     g = open("./input2.pig", "w")
#     var_types = ["bv8", "bv16", "bv32", "bv64"]
#     var_nums = random.randint(1, 5)
#     for i in range(0, var_nums):
#         var_name = f"v00{i}"
#         var_type = random.choice(var_types)
#         bits = int(var_type[2:])
#         stmt = f"D {var_type} {var_name}"
#         print(stmt, file=f)
#         print(stmt, file=g)
#         val = random.choice(["0", "1"]) * bits
#         stmt = f"A {var_name} ( {val} )"
#         print(stmt, file=f)
#         print(stmt, file=g)
#     for i in range(0, var_nums):
#         var_name = f"v00{i}"
#         stmt = f"O {var_name}"
#         print(stmt, file=f)
#         print(stmt, file=g)

import random

all_length =0

def random_bits(value_type):
    bits = int(value_type[2:])
    return ''.join(random.choice(['0', '1']) for _ in range(bits))

def random_expression(variables, variable_types, depth=0, max_depth=5):
    max_depth = random.randint(1, 6)
    if depth >= max_depth:
        var = random.choice(variables)
        return f"( {var[1]} )"
    # 随机选择一个表达式类型
    expression_type = random.choice(['value', 'unary', 'binary'])
    if expression_type == 'value':
        if random.random() < 0.5:
            var = random.choice(variables)
            var_type = variable_types[var[1]]
            return f"( {random_bits(var_type)} )"
        else:
            var = random.choice(variables)
            return f"( {var[1]} )"
    elif expression_type == 'unary':
        # 生成一个一元运算表达式
        return f"( ! {random_expression(variables, variable_types, depth + 1, max_depth)} )"
    else:
        # 生成一个二元运算表达式
        op = random.choice(['+', '-', '&', '|'])  # 包括 ADD (+), SUB (-), AND (&), OR (|)
        var1 = random_expression(variables, variable_types, depth + 1, max_depth)
        var2 = random_expression(variables, variable_types, depth + 1, max_depth)
        return f"( {var1} {op} {var2} )"
    

def declare(n,var_types,variables_dict,variable_types):
    declarations = []
    available_keys = list(variables_dict.keys())
    if not available_keys:  # 检查列表是否为空
        print("No variables available for declaration.")
        return declarations,0  # 如果字典为空，直接返回空列表
    for _ in range(min(n, len(available_keys))):
        #不知道这里为什么有IndexError: list index out of range的bug
        # print(variables_dict)
        var_name = random.choice(list(variables_dict.keys()))
        var_type = random.choice(var_types)
        variables_dict.pop(var_name)
        variable_types[var_name] = var_type
        declarations.append((f"D {var_type} {var_name}",var_name))
    return declarations, min(n, len(available_keys))

def assign(variables,variable_types):
    if not variables:
        return []
    var = random.choice(variables)
    # var_type = variable_types[var]
    expr = random_expression(variables, variable_types)
    return [f"A {var[1]} {expr}"]

def output(variables):
    if not variables:
        return []
    var = random.choice(variables)
    return [f"O {var[1]}"]


def remove(variables, variable_types, variables_dict,removed_variables=None):
    if removed_variables is None:
        removed_variables = set()

    removals = []
    for var in variables:
        var_name = var[1]  # 假设 var 是一个元组，其中 var[1] 是变量名
        if var_name in variable_types and var_name not in removed_variables:
            # 从变量类型字典中移除变量类型信息
            var_type = variable_types.pop(var_name, None)
            # 如果需要，可以将变量重新添加到另一个字典中，这里假设不需要
            # variables_dict[var_name] = var_type  # 仅当你需要保持这个信息时
            removals.append(f"R {var_name}")
            # 记录已移除的变量，防止再次移除
            removed_variables.add(var_name)
    return removals


def B(actual,n,variables,variable_types):
    target_line = f"{ actual+n:03d}"
    expr = random_expression(variables, variable_types)
    return [f"B {target_line} {expr}"]

def if_block(var_types,variables_dict,variable_types, max_depth):
    global all_length
    if all_length >= 900:
        return [], 0
    length2 = 0
    n1 = random.randint(1, 5)
    if 2*n1 < max_depth:
        variables, n1 = declare(n1,var_types,variables_dict,variable_types)
        code = [var[0] for var in variables]
        all_length += n1
        n2 = random.randint(1, 5)
        if n2+1 < max_depth - 2*n1 :
            code.extend(B(all_length,n2,variables,variable_types))
            for i in range(n2):
                if random.random()<0.5:
                    code.extend(assign(variables,variable_types))
                else:
                    code.extend(output(variables))
            all_length += n2+1
            code.extend(remove(variables, variable_types, variables_dict))
            length2 = 2*n1 + n2+1
            all_length +=n1
            return code, length2
        else:
            code.extend(remove(variables, variable_types, variables_dict))
            length2 = 2*n1 
            all_length +=n1
            return code, length2
    else:
        return [],0

def for_block(var_types,variables_dict,variable_types, max_depth):
    global all_length
    if all_length >= 900:
        return [], 0
    length2 = 0
    n1 = random.randint(1, 5)
    if 2*n1 < max_depth :
        variables,n1 = declare(n1,var_types,variables_dict,variable_types)
        code = [var[0] for var in variables]
        all_length += n1
        n2 = random.randint(1, 5)
        if n2+1 < max_depth - 2*n1 :
            for i in range(n2):
                if random.random() < 0.5:
                    code.extend(assign(variables,variable_types))
                else:
                    code.extend(output(variables))
            all_length += n2
            code.extend(B(all_length-n2,n2,variables,variable_types))
            all_length+=1
            code.extend(remove(variables, variable_types, variables_dict))
            length2 = 2*n1 + n2+1
            all_length +=n1
            return code,length2
        else:
            code.extend(remove(variables, variable_types, variables_dict))
            length2 = 2*n1
            all_length +=n1
            return code,length2
    else:
        return [],0



def basic_block(var_types,variables_dict,variable_types,max_depth,recursion_depth=0):
    global all_length
    if all_length >= 900 or recursion_depth >= 2:
        return [], 0
    depth = 0
    n = random.randint(1, 5)  # Number of variables to declare
    if 2*n < max_depth:
        variables,n = declare(n,var_types,variables_dict,variable_types)
        code = [var[0] for var in variables]
        all_length +=n
        if max_depth-2*n > 0:
            iter_num = random.randint(1, max_depth-2*n)  # Number of statements in the loop
            for i in range(iter_num):
                if recursion_depth >= 1:
                    break
                block_type = random.choice(["BASIC_BLOCK", "IF_BLOCK", "FOR_BLOCK", "ASSIGN_BLOCK", "OUTPUT_BLOCK"])
                if block_type == "BASIC_BLOCK":
                    
                    code1,depth1 = basic_block(var_types,variables_dict,variable_types,iter_num-i,recursion_depth + 1)
                    # code.extend("ba-ba")
                    code.extend(code1)
                    i += depth1 
                    
                    recursion_depth +=1
                elif block_type == "IF_BLOCK":
                    
                    code1,depth1 = if_block(var_types,variables_dict,variable_types,iter_num-i)
                    # code.extend("ba-if")
                    code.extend(code1)
                    i += depth1 
                    
                    # recursion_depth +=1
                elif block_type == "FOR_BLOCK":
                    
                    code1,depth1 = for_block(var_types,variables_dict,variable_types,iter_num-i)
                    # code.extend("ba-for")
                    code.extend(code1)
                    i += depth1 
                    # recursion_depth +=1
                elif block_type == "ASSIGN_BLOCK":
                    
                    code.extend(assign(variables,variable_types)) #one line
                    all_length += 1
                elif block_type == "OUTPUT_BLOCK":
                    
                    code.extend(output(variables)) #one line
                    all_length += 1

            code.extend(remove(variables, variable_types, variables_dict))
            depth = 2*n + iter_num
            all_length += n
            
            return code,depth
        else:

            code.extend(remove(variables, variable_types, variables_dict))
            depth = 2*n
            all_length += n
            return code,depth
    
    else:
        return [],depth



def generate_program(file_path, max_lines=1000, max_length=1000):
    global all_length
    max_depth = random.randint(100,900)
    var_types = ["bv8", "bv16", "bv32", "bv64"]
    variables_dict = {f"v{i:03d}": None for i in range(1000)}
    variable_types = {}
    n1 = random.randint(1,5)  # Number of variables to declare
    variables,n1 = declare(n1,var_types,variables_dict,variable_types)
    code = [var[0] for var in variables]#不确定是0还是1
    all_length = n1
    iter_num = random.randint(1, max_depth-2*n1)
    for i in range(iter_num):
        if all_length >= 900-n1:
            break
        block_type = random.choice(["BASIC_BLOCK", "IF_BLOCK", "FOR_BLOCK", "ASSIGN_BLOCK", "OUTPUT_BLOCK"])
        if block_type == "BASIC_BLOCK":
            
            code1,depth1 = basic_block(var_types,variables_dict,variable_types,iter_num-i)
            code.extend(code1)
            i += depth1 
        elif block_type == "IF_BLOCK":
            
            code1,depth1 = if_block(var_types,variables_dict,variable_types,iter_num-i)
            code.extend(code1)
            i += depth1          
        elif block_type == "FOR_BLOCK":
            
            code1,depth1 = for_block(var_types,variables_dict,variable_types,iter_num-i)
            code.extend(code1)
            i += depth1           
        elif block_type == "ASSIGN_BLOCK":
            code.extend(assign(variables,variable_types)) #one line
            all_length +=1
        elif block_type == "OUTPUT_BLOCK":
            code.extend(output(variables)) #one line
            all_length +=1
    code.extend(remove(variables, variable_types, variables_dict))        
     # Write to file
    with open(file_path, "w") as file:
        for line in code:
            print(line, file=file)


def adjust_input_file(original_file, new_file):
    with open(original_file, 'r') as file:
        lines = file.readlines()

    # 分类语句
    d_statements = []
    r_statements = []
    other_statements = []
    branch_updates = {}
    original_line = {}
    # 分类处理
    i = 0
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('D '):
            d_statements.append(stripped_line)
        elif stripped_line.startswith('R '):
            r_statements.append(stripped_line)
        elif stripped_line.startswith('B '):
            parts = line.split()
            branch_updates[i] = int(parts[1])
            other_statements.append(stripped_line)
        else:
            other_statements.append(stripped_line)
        i += 1
    # 构建新的文件内容
    new_content = d_statements + other_statements + r_statements


    # 将原始行号映射到新的行号
    original_to_new_line_numbers = {}
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line in new_content:
            original_to_new_line_numbers[i] = new_content.index(stripped_line)
    # print(original_to_new_line_numbers)
    # print(branch_updates)


    # 更新分支行
    # print(branch_updates.items())
    for index, original_target in branch_updates.items():
        new_target = original_to_new_line_numbers[original_target]
        new_B = original_to_new_line_numbers[index]
        parts = new_content[new_B].split()
        new_content[new_B] = f"{parts[0]} {new_target:03d} {' '.join(parts[2:])}"

    # 写入新文件
    with open(new_file, 'w') as file:
        for line in new_content:
            print(line, file=file)


if __name__ == "__main__":
    input_file_path = "./input1.pig"
    output_file_path = "./input2.pig"
    generate_program(input_file_path)
    adjust_input_file(input_file_path, output_file_path)

# if __name__ == "__main__":
#     generate_program("./input.pig")


