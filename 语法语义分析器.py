import os

start_symbol = ""  # 初始符号
symbol = set()  # 所有符号集合
terminal_symbol = set()  # 终结符集合
non_terminal_symbol = set()  # 非终结符集合

产生式 = []  # {'left': "S'", 'right': ['S']}
项目 = []  # {'left': "S'", 'right': ['S'], 'point': 0}
新项目 = []  # {'left': "S'", 'right': ['S'], 'point': 0, "origin": 0, "accept": "#"}
首项 = {}  # 每个非终结符B的形如B→·C的产生式的序号 首项['S']={2, 5}

closure = []  # 每个项目的闭包 closure[0]={0, 2, 5, 7, 10}
closureSet = []  # 项目集族 closureSet[0]={0, 2, 5, 7, 10}

goto = [] # go[状态i][符号j] 该数组依次存储了不同内容，分别为： 
# = Closure{项目x, 项目y}
# = {项目x, 项目y, 项目z}
# = 状态k
# 进入Action/Goto环节后，go函数会被转换为goto函数
# goto[状态i][符号j]=0:accept / +x:移进字符和状态x（sx）/ -x:用产生式x归约（rx）/ 无定义:err


first = {} # first['F']={'(', 'a', 'b', '^'}
first_empty = []  # first集中含有空的非终结符集合 {"E'", "T'", "F'"}

gotoFile = open(r'output\\goto.txt', 'w', encoding="utf-8")
firstFile = open(r'output\\first.txt', 'w', encoding="utf-8")
productionFile = open(r'output\\production.txt', 'w', encoding="utf-8")
closureFile = open(r'output\\closure.txt', 'w', encoding="utf-8")
lrFile = open(r'output\\lr.txt', 'w', encoding="utf-8")
analyzeFile = open(r'output\\analyze.txt', 'w', encoding="utf-8")
xmjzFile = open(r'output\\xmjz.txt', 'w', encoding="utf-8")
emitFile = open(r'output\\emit.txt', 'w', encoding="utf-8")
varFile = open(r'output\\var.txt', 'w', encoding="utf-8")


# 传入项目集(列表，内含项目编号)，推得其closure；判断是否已存在
# 若不存在，命名新项目集族，并求Goto。
def find_Goto(i):
    global symbol, closure
    #print(i)
    for j in closureSet[i]:
        #print("  ", j)
        item = 新项目[j]
        try:
            nowCharacter = item["right"][item["point"]]
            if nowCharacter in goto[i]:
                goto[i][nowCharacter].append(j + len(terminal_symbol))
            else:
                goto[i][nowCharacter] = [j + len(terminal_symbol)]
        except:
            pass
    for j in symbol:
        if j in goto[i]:  # goto(i, j)
            newSet = set()
            for itemOrd in goto[i][j]:
                newSet |= closure[itemOrd]
            print("Goto(I%d,%s) = Closure(" % (i, j), goto[i][j], ') =', newSet, "={", end=" ", file=gotoFile)
            for k in newSet:
                print(新项目[k]["left"], "->", ''.join(新项目[k]["right"]), ",", 新项目[k]["accept"], end=" ", sep="", file=gotoFile)
            print("}", end=" ", file=gotoFile)
            #print("len(ClosureSet)=", len(closureSet))
            if newSet in closureSet:
                goto[i][j] = closureSet.index(newSet)
            else:
                closureSet.append(newSet)
                goto.append({})
                goto[i][j] = len(closureSet) - 1
            print('= I', goto[i][j], sep="", file=gotoFile)
    print(i, closureSet[i], file=xmjzFile)


# 求项目i的Closure
def find_closure(i, ini):
    #print("find_closure", i)
    global closure
    #if len(closure[i]) > 0:
    #    return closure[i]

    item = 新项目[i]
    try:
        nowCharacter = item["right"][item["point"]]
        beta = ""
        alpha = item["accept"]
        fir = set()
        try:
            beta = item["right"][(item["point"] + 1):]
            beta += [alpha]
            for sym in beta:
                fir |= first[sym]
                if sym not in first_empty:
                    break
        except:
            fir = set(alpha)
        if nowCharacter in 首项:
            for j in 首项[nowCharacter]:
                if j not in closure[ini] and 新项目[j]["accept"] in fir:
                    #print(j)
                    closure[i].add(j)
                    closure[ini].add(j)
                    closure[i] |= find_closure(j, ini)
    except:
        closure[i].add(i)
        return {i}
    return closure[i]


with open("input\产生式.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip().replace('\n', ' ')
        #print(line)
        if line == "":
            continue
        line = line.split(':')
        if len(line) < 3:
            continue
        terminal_symbol.add(line[1])
        symbol.add(line[1])
        if line[2] == '$':
            产生式.append({"left": line[1], "right": [], "order":int(line[0])})
        else:
            产生式.append({"left": line[1], "right": line[2].split(' '), "order":int(line[0])})
            symbol |= (set(line[2].split(' ')))

start_symbol = 产生式[0]["left"]
symbol |= terminal_symbol
symbol -= {''}
terminal_symbol -= {''}
non_terminal_symbol = terminal_symbol
terminal_symbol = symbol - non_terminal_symbol
terminal_symbol |= {'#'}

#print(产生式)

#求First集
for item in non_terminal_symbol:
    first[item] = set()
for item in terminal_symbol:
    first[item] = {item}

bfs = []
for item in 产生式:
    try:
        sym = item["right"][0]
        if sym in terminal_symbol:
            first[item["left"]].add(sym)
    except:
        first_empty.append(item["left"])
        bfs.append(item["left"])

import copy

proCopy = copy.deepcopy(产生式)
while len(bfs) > 0:
    sym = bfs.pop(-1)
    for i, item in zip(range(len(proCopy)), proCopy):
        if item["left"] == sym:
            proCopy[i]["right"] = []
        elif sym in item["right"]:
            proCopy[i]["right"].remove(sym)
            if len(proCopy[i]["right"]) == 0:
                if item["left"] not in first_empty:
                    first_empty.append(item["left"])
                    bfs.append(sym)

print(first_empty, file=firstFile)

f = 1
while f:
    f = 0
    for item in 产生式:
        for sym in item["right"]:
            if not first[item["left"]].issuperset(first[sym]):
                f = 1
                first[item["left"]] |= first[sym]
            if sym not in first_empty:
                break
    #print(first, "\n")

for item in non_terminal_symbol:
    print("%s\n%s" % (item, " ".join(list(first[item]))), " $" if item in first_empty else "", "\n", file=firstFile)

# 从产生式生成项目
for order, i in zip(range(len(产生式)), 产生式):
    for j in range(len(i["right"]) + 1):
        项目.append({"left": i["left"], "right": i["right"], "order":i["order"], "point": j, "origin": order, "isTer": (j == len(i["right"]))})

# 从项目生成带接受符号的项目
for i, item in zip(range(len(项目)), 项目):
    for sym in terminal_symbol:
        closure.append(set())
        新项目.append(copy.deepcopy(item))
        新项目[-1]["accept"] = sym

# 记录首项
for i, item in zip(range(len(新项目)), 新项目):
    if item["point"] == 0:
        if item["left"] in 首项:
            首项[item["left"]].add(i)
        else:
            首项[item["left"]] = {i}

print("项目：\n", 项目, "\n", file=productionFile)
print("新项目：\n", 新项目, "\n", file=productionFile)
print("原点在开头的产生式编号：\n", 首项, "\n", file=productionFile)

#print(新项目)

#求每个项目的闭包
print("单个项目的闭包：", file=closureFile)
for i, item in zip(range(len(新项目)), 新项目):
    print("%-4d " % i, item, file=closureFile)
    closure[i].add(i)
    closure[i] = find_closure(i, i)
    if item["origin"] == 0 and item["accept"] == '#' and item["point"] == 0:
        closureSet.append(closure[i])
    print("  ", closure[i], file=closureFile)

#print(closureSet[0])
goto.append({})

print("Goto：", file=gotoFile)
i = 0
while (i < len(closureSet)):
    find_Goto(i)
    i += 1
    print(file=gotoFile)

print("LR(1)分析器：", file=lrFile)
ts = sorted(list(terminal_symbol - {start_symbol}))
nts = sorted(list(non_terminal_symbol - {start_symbol}))
print("   ", '  '.join(map(lambda x: (x + "  ")[:3], ts)), "", '  '.join(map(lambda x: (x + "  ")[:3], nts)), file=lrFile)
for i in range(len(closureSet)):
    print("%-3d" % i, end=" ", file=lrFile)
    for item in closureSet[i]:
        k = item
        item = 新项目[item]
        if item["isTer"] == True:
            if item["accept"] in goto[i]:
                print("error!", "%d号项目集族的\t%s\t符号冲突，冲突的产生式为\t%d\t" % (i, item["accept"], k), 新项目[k])
                '''
                print("项目集族为：")
                for t in closureSet[i]:
                    print(t, 新项目[t])
                    '''
            else:
                goto[i][item["accept"]] = -item["origin"]
    for j in ts:
        try:
            if goto[i][j] > 0:
                print("s%-3d" % goto[i][j], end=" ", file=lrFile)
            if goto[i][j] < 0:
                print("r%-3d" % -goto[i][j], end=" ", file=lrFile)
            if goto[i][j] == 0:
                print("acc ", end=" ", file=lrFile)
        except:
            print("    ", end=" ", file=lrFile)
    for j in nts:
        try:
            print("%-4d" % goto[i][j], end=" ", file=lrFile)
        except:
            print("    ", end=" ", file=lrFile)
    print(file=lrFile)

names = ""
with open('intermediate\\names.txt', encoding="utf-8") as f:
    names = f.read()
names = names.strip().replace(' ', "").split('\n')
names = names[::-1]
names = list(filter(lambda x: x != "", names))
# print(names)
inp = "" # 分析栈
with open("intermediate\\processed_sourceCode.txt", encoding="utf-8") as f:
    inp = f.read()
inp = inp.strip().split('\n')
inp = list(filter(lambda x: x != "", inp))
inp += ['#']
print(inp, "的分析栈：", file=analyzeFile)
statusStack = [0] # 状态栈
charStack = ['#'] # 输入栈
tempVarCnt = {}
midCode = {}

pointer = 0
tree = []
for i in range(len(closureSet)):
    tree.append({})

def prin(num, typ, ss = 0):
    if ss == 0:
        global attr
        ss = attr[typ]
    if type(num) == int:
        num = charStack[num]
    print(num,".%s="%typ, ss, sep="", file=analyzeFile)

def getAttr(nam):
    global varStack
    global domain
    if (nam, domain) in varStack:
        return varStack[nam, domain]
    elif domain != 0 and (nam, 0) in varStack:
        return varStack[nam, 0]
    else:
        print("Error: undefined variable %s"%nam)
        a = [] # try catch 捕捉到错误，程序停止分析
        print(a[2])

def emit(*args):
    global emitCount
    args = list(map(lambda x: str(x),args))
    lis = []
    if len(args) == 1:
        lis = [args[0], '-', '-', '-']
    else:
        lis = args[:-1]
        for i in range(4 - len(args)):
            lis.append('-')
        lis.append(args[-1])
    if domain in midCode:
        midCode[domain].append(copy.deepcopy(lis))
    else:
        midCode[domain] = [copy.deepcopy(lis)]
    print("(%-6s , %2d) ("%(str(domain), len(midCode[domain])), ','.join(lis),")", sep="", file=emitFile)

def getNumType(num):
    return str(type(num))[8:-2]

def newTempVar(typ):
    cnt = 0
    if domain in tempVarCnt:
        cnt = tempVarCnt[domain]
    cnt += 1
    tempVarCnt[domain] = cnt
    cnt = "$%d"%cnt
    varStack[cnt, domain] = {"type":typ, "is_temp":True}
    print("新增临时变量：name=%s, 作用域=%s, type=%s, 临时变量=%s"%(cnt, str(domain), typ, "True"), file=analyzeFile)
    return cnt

def getType(nam):
    if type(nam) == str:
        return getAttr(nam)["type"]
    else:
        return getNumType(nam)

def getDomain(nam):
    global domain
    global varStack
    if type(nam) == str:
        if (nam, domain) in varStack:
            return domain
        elif domain != 0 and (nam, 0) in varStack:
            return 0
        else:
            print("Error: undefined variable %s"%nam)
            a = [] # try catch 捕捉到错误，程序停止分析
            print(a[2])
    else:
        return domain
        

varStack = {} # varStack[name,作用域] = {type:"int"/数值, is_temp=True, value=NULL}
funStack = {} # funStack[过程名]= {code:四元式组, var=[接受的参数], ret_type="int"}
domain = 0 # 一个全局变量记录当前作用域，初始为int(0)，为全局；否则为过程名（string）
root = -1
cntNode = -1
nodeStack = [] # 语法树结点 nodeStack[cntNode]["name"]="123" nodeStack[cntNode]["children"]=[1, 2, 3]
attrStack = []
procedureType = {}

print("%-10s %-10s %-10s" % (' '.join(map(lambda x: str(x), statusStack)), ' '.join(charStack), ' '.join(inp[pointer:])), file=analyzeFile)
while True:
    # print(attrStack)
    c = inp[pointer]
    try:
        #print(c)
        #print(statusStack[-1])
        num = goto[statusStack[-1]][c]
        if num == 0:
            print("Accepted", file=analyzeFile)
            tree[statusStack[-1]]["name"] = charStack[-1]
            root = statusStack[-1]
            break
        elif num > 0: # 移进
            statusStack.append(num)
            #print(num, c)
            tree.append({})
            cntNode += 1
            tree[cntNode]["name"] = c
            nodeStack.append(cntNode)
            attrStack.append({})
            charStack.append(c)
            pointer += 1

            if c in ["identifier", "number"]:
                tree[cntNode]["children"] = [cntNode + 1]
                tree.append({})
                cntNode += 1
                nam = names.pop()
                tree[cntNode]["name"] = nam
                if c == "identifier":
                    attrStack[-1]["name"] = nam
                    print("用identifier归约:", file=analyzeFile)
                    prin(-1, "name", nam)
                    
                elif c == "number":
                    attrStack[-1]["name"] = eval(nam)
                    #attrStack[-1]["type"] = str(type(attrStack[-1]["name"]))[8:-2]
                    print("用number归约:", file=analyzeFile)
                    prin(-1, "name", nam)
                    #prin(-1, "type", attrStack[-1]["type"])

        elif num < 0:
            item = 产生式[-num]  # 用 item 归约
            print("\n用%d号产生式归约:"%(item["order"]), item["left"], "→", " ".join(item["right"]), file=analyzeFile)
            order = item["order"]
            attr = {}
            # 归约前执行的
            
            if order in [117, 617]:
                attr["name"]=attrStack[-1]["name"]
                prin(-1, "name")
                varStack[attr["name"], domain] = {"type":attrStack[-2]["type"], "is_temp":False}
                print("读入新变量：name=%s, 作用域=%s, type=%s, 临时变量=%s"%(attr["name"], str(domain), str(attrStack[-2]["type"]), "False"), file=analyzeFile)
            elif order == 118:
                attr["type"]=attrStack[-3]["type"]
                prin(-3, "type")
            elif order == 121:
                attr["name"]=attrStack[-1]["name"]
                prin(-1, "name")
            elif order in [122, 416, 414, 412, 407, 405, 403, 401, 132, 131]:
                attr["name"]=attrStack[-1]["name"]
                prin(-1, "name")
            elif order in [113, 724]:
                attr["name"]=attrStack[-3]["name"] # a
                prin(-3, "name")
                attr["value"]=attrStack[-1]["name"] # 5.123 "$1"
                prin(-1, "value")
                attr["type"]=getType(attr["value"]) # float
                prin(-1, "type", attr["type"])
                op = "="
                if order == 724:
                    op = attrStack[-2]["operator"]
                if op == "=":
                    op = ":="
                shouldType = getType(attr["name"])
                if shouldType != attr["type"]:
                    print("Warning: 类型不匹配。变量%s的类型为%s，赋值%s的类型为%s"%(attr["name"], shouldType, str(attr["value"]), attr["type"]))
                #if shouldType == "int":
                #    attr["value"] = int(attr["value"])
                varStack[attr["name"], getDomain(attr["name"])]["value"] = attr["value"]
                #print("(%s,%s).value=%s"%(attr["name"], str(domain), attr["value"]))
                print("(%s,%s).value=%s"%(attr["name"], str(domain), attr["value"]), file=analyzeFile)
                
                emit(op, attr["value"], attr["name"])
            elif order == 602:
                domain = attrStack[-1]["name"]
                procedureType[domain] = attrStack[-2]["type"]
                midCode[domain] = []
                print("新函数：%s type=%s"%(domain, procedureType[domain]), file=analyzeFile)
            elif order in [411, 413, 402, 404, 406]:
                op = attrStack[-2]["operator"]
                lop = attrStack[-3]["name"]
                ltype = getType(lop)
                rop = attrStack[-1]["name"]
                rtype = getType(rop)
                newTempType = "void"                
                if ltype == rtype:
                    newTempType = ltype 
                else:
                    newTempType = "float"
                    print("Warning: 类型不匹配。左操作数%s的类型为%s，右操作数%s的类型为%s"%(lop, ltype, rop, rtype))
                if order in [402, 404, 406]:
                    newTempType = "int"
                newTempName = newTempVar(newTempType)
                emit(op, lop, rop, newTempName)
                attr["name"] = newTempName
                prin("expression", "name", newTempName)
            elif order == 415:
                op = "!"
                rop = attrStack[-1]["name"]
                rtype = getType(rop)
                newTempType = "int"
                newTempName = newTempVar(newTempType)
                emit(op, rop, newTempName)
                attr["name"] = newTempName
                prin("!_expression", "name", newTempName)

            elif order in [511, 512, 513, 514]:
                attr["operator"]=charStack[-1]
                prin(-1, "operator", attr["operator"])
            elif order == 731:
                typPro = procedureType[domain]
                namExp = attrStack[-2]["name"]
                typExp = getType(namExp)
                if typPro != typExp:
                    print("Warning: 类型不匹配。函数%s的类型为%s，返回值%s的类型为%s"%(str(domain), typPro, namExp, typExp))
                emit("return", namExp)
            elif order == 732:
                emit("return")
            elif order == 141:
                #print(attrStack[-2]["name"])
                for name in attrStack[-2]["name"]:
                    emit("param", name, '-', '-')
                nam = attrStack[-4]["name"]
                #procedureType["program"] = "int"
                #procedureType["demo"] = "int"
                typ = procedureType[nam]
                if typ != "void":
                    newVarNam = newTempVar(typ)
                    emit("call", nam, newVarNam)
                    attr["name"] = newVarNam
                    prin("function_expression", "name", attr["name"])
                else:
                    emit("call", nam, "-", "-")
            elif order in [154, 152]:
                attr["name"] = []
                prin("expression_list", "name", attr["name"])
            elif order in [153, 151]:
                #print(attrStack[-1]["name"])
                #print(attrStack[-2]["name"])
                attr["name"] = [attrStack[-2]["name"]] + attrStack[-1]["name"] 
                #print(attr["name"])
                prin("expression_list", "name", attr["name"])
            elif order in [723, 726]: # 参照154
                attr["name"] = []
                prin("assignment_expression_list", "name", attr["name"])
            elif order in [725, 722]: # 参照153
                attr["name"] = [attrStack[-2]["name"]] + attrStack[-1]["name"] 
                prin("assignment_expression_list", "name", attr["name"])
                

            elif order in [201, 202, 203, 204, 205, 206, 207, 208, 209]:
                attr["operator"] = charStack[-1]
                prin(-1, "operator", attr["operator"])
            elif order in [501, 502, 503, 504, 505, 506, 507, 508]:
                attr["operator"] = charStack[-1]
                prin
            elif order == 123:
                attr["name"] = attrStack[-2]["name"]
                prin(-2, "name")
            elif order == 751:
                emit("j=", attrStack[-2]["name"], 0, "unknown")
                attr["pos"] = len(midCode[domain])
                prin("M_selection_statement", "pos", attr["pos"])
            elif order in [742, 741, 743]:
                if order == 743:
                    emit("j", attrStack[-6]["pos"] + 1)
                midCode[domain][attrStack[-2]["pos"] - 1][3] = str(len(midCode[domain]) + 1)
                prin("回填", "产生式序号", attrStack[-2]["pos"])
                prin("回填", "值", str(len(midCode[domain]) + 1))
                print("    Modify:(%-6s , %2d) ("%(str(domain), attrStack[-2]["pos"]), ','.join(midCode[domain][attrStack[-2]["pos"] - 1]),")", sep="", file=emitFile)
            elif order == 752:
                emit("j", "unknown")
                midCode[domain][attrStack[-3]["pos"] - 1][3] = str(len(midCode[domain]) + 1)
                prin("回填", "产生式序号", attrStack[-3]["pos"])
                prin("回填", "值", str(len(midCode[domain]) + 1))
                print("    Modify:(%-6s , %2d) ("%(str(domain), attrStack[-3]["pos"]), ','.join(midCode[domain][attrStack[-3]["pos"] - 1]),")", sep="", file=emitFile)
                attr["pos"] = len(midCode[domain])
                prin("N_selection_statement", "pos", attr["pos"])
            elif order == 753:
                attr["pos"] = len(midCode[domain])
                prin("N_iteration_statement", "pos", attr["pos"]) 






            if item["right"] == []:  # 空
                charStack += [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = [cntNode + 1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []
                tree[cntNode]["name"] = ''

            else:
                k = len(item["right"])
                statusStack = statusStack[:-k]
                charStack = charStack[:-k] + [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])
                #print(statusStack[-1])
                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []

                for i in range(k):
                    nowNode = nodeStack.pop()
                    attrStack.pop()
                    tree[cntNode]["children"].append(nowNode)

                tree[cntNode]["children"] = tree[cntNode]["children"][::-1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)
            # 归约后执行的
            type_specifier = {301:"int", 302:"double", 303:"float", 304:"void"}
            if order in type_specifier:
                typ = type_specifier[order]
                attr["type"] = typ
                prin(-1, "type")
            elif order == 112:
                attr["type"] = attrStack[-1]["type"]
                prin(-1, "type")
            elif order == 601:
                print("%s函数结束，domain=0"%(domain), file=analyzeFile)
                domain = 0
                
            
            attrStack.append(attr)
    except Exception as e:
        print(e)
        print("error", file=analyzeFile)
        break
    print("%-10s \t\t %-10s \t\t %-10s" % (' '.join(map(lambda x: str(x), statusStack)), ' '.join(charStack), ' '.join(inp[pointer:])), file=analyzeFile)

for item in varStack:
    print(item, varStack[item], file=varFile)


def outp(now):
    #print(now)
    if not tree[now]:
        return {}
    di = {}
    di["name"] = tree[now]["name"].replace("_", "_  \n") + ' '

    di["children"] = []
    if ("children" not in tree[now]) or (not tree[now]["children"]):
        return di
    for child in tree[now]["children"]:
        di["children"].append(outp(child))

    #print(now, di)
    return di


# print(root)
outpTree = outp(cntNode)
#print(outpTree)

from pyecharts import options as opts
from pyecharts.charts import Tree

treeData = [outpTree]
c = (
    Tree().add(
        "",
        treeData,
        orient="TB",
        initial_tree_depth=-1,
        #collapse_interval=10,
        symbol_size=3,
        is_roam=True,
        edge_shape="polyline",
        #is_expand_and_collapse=False,
        label_opts=opts.LabelOpts(
            position="top",
            horizontal_align="right",
            vertical_align="middle",
            #rotate='15',
            font_size=15)).set_global_opts(title_opts=opts.TitleOpts(title="语法树")).render("output\语法树.html"))
