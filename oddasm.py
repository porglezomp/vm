from __future__ import print_function

import time
import sys

HZ = 1024
N_REGISTERS = 8
N_STACK = 1024
sp = 0
pc = 0

MOV = 0
BR = 1
ADD = 2
SUB = 3
STR = 4
LDR = 5
PUT = 6
PUSH = 7
POP = 8
EQ = 9
NE = 10
LT = 11
GT = 12
EZ = 13
INT = 14
NL = 15

instructions = {
    "mov": MOV,  "br": BR, "add": ADD, 
    "sub": SUB, "str": STR, "ldr": LDR,
    "put": PUT, "push": PUSH, "pop": POP, 
    "eq": EQ, "ne": NE, "lt": LT,
    "gt": GT, "ez": EZ, "int": INT,
    "nl": NL
}

code = []
stack = []
asm = """
start:
mov r0, 0

loop:
ldr r1, r0

ez r1
br end

add r0, r0, 1
put r1
br loop
end:
ldr r0, 42
put r0
"""


# push val:
# add sp, sp, 1
# str val, sp

# pop val:
# ldr dest, sp
# sub sp, sp, 1
fibo = """
fib:
add sp, sp, 1
str lr, sp

ez r0
br endfib
lt r0, 3
br one

sub r0, r0, 1
add sp, sp, 1
str r0, sp

mov lr, pc
add lr, lr, 2
br fib

mov r2, r0
ldr r0, sp
str r2, sp
sub r0, r0, 1

mov lr, pc
add lr, lr, 2
br fib

ldr r2, sp
sub sp, sp, 1
add r0, r0, r2
br endfib

one:
mov r0, 1
br endfib

endfib:
ldr lr, sp
sub sp, sp, 1
mov pc, lr

start:
mov r0, 13

mov lr, pc
add lr, lr, 2
br fib

put r0
nl

"""

def parse(string):
    # Ensure that all labels will get split onto their own lines
    string = string.replace(":", ":\n")
    lines = string.split("\n")
    # Remove blank lines from the source
    lines = [line.strip() for line in lines if line.strip() != ""]
    
    labels = {}
    code = []
    i = 0

    for line in lines:
        if ":" in line:
            # Add the location of the label to the label table
            labels[line.strip(":")] = i
        else:
            ls = line.split(" ", 1)
            if len(ls) > 1:
                [op, args] = ls
            else:
                op = ls[0]
                args = ""
            op = op.lower()
            # Only accept valid opcodes
            if op not in instructions:
                raise SyntaxError("Unknown opcode '{}'".format(op.upper()))
            # Convert the opcodes into the integer versions
            op = instructions[op]

            # Split the arg list
            args = [arg.strip() for arg in args.split(",")]

            # Return an instruction
            instr = (op, args)
            code.append(instr)

            # Increment the location
            i += 1

    final_code = []
    for op, args in code:
        args = [replaceall(arg, labels) for arg in args]

        # Return an instruction
        instr = (op, args)
        final_code.append(instr)

    return final_code, labels

def replaceall(string, toreplace):
    if string in toreplace:
        return str(toreplace[string])
    return string
    # for k in toreplace.keys():
    #     string = string.replace(str(k), str(toreplace[k]))
    # return string

def isregister(string):
    if string == "pc" or string == "sp" or string == "lr":
        return True
    try:
        if string[0] == 'r' and 0 <= int(string[1:]) < N_REGISTERS:
            return True
    except:
        return False
    return False

LR = N_REGISTERS - 3
SP = N_REGISTERS - 2
PC = N_REGISTERS - 1
def rnum(regstr):
    if regstr == "lr":
        return LR
    if regstr == "sp":
        return SP
    if regstr == "pc":
        return PC
    return int(regstr[1:])

def register_value(registers, regstr):
    if isregister(regstr):
        return registers[rnum(regstr)]
    else:
        return int(regstr)

def register_values(registers, regstrs, *args):
    results = []
    for arg in args:
        results.append(register_value(registers, regstrs[arg]))
    return tuple(results)

# MOV, BR, ADD, SUB, STR, LDR, PUT, EQ, NE, LT, GT, EZ
# Unimplemented: PUSH, POP, INT
registers = [0 for item in range(N_REGISTERS)]
stack = [0 for item in range(N_STACK)]
stack[0:len("Hello, World!")] = "Hello, World!"
stack[42] = "\n"
def run(init_pc, code):
    global registers
    global stack
    registers[PC] = init_pc
    value = lambda x: register_value(registers, x)
    while True:
        if registers[PC] >= len(code):
            return

        op, args = code[registers[PC]]
        arg_values = lambda *x: register_values(registers, args, *x)

        if op == MOV:  # MOV <dest> <src>
            if not isregister(args[0]):
                raise SyntaxError("MOV must mov into register")
            registers[rnum(args[0])] = value(args[1])

        elif op == BR:  # BR <loc>
            registers[PC] = value(args[0]) - 1

        elif op == ADD:  # ADD <dest> <rval0> <rval1>
            if not isregister(args[0]):
                raise SyntaxError("ADD must add into register")
            a, b = arg_values(1, 2)
            registers[rnum(args[0])] = a + b

        elif op == SUB:  # SUB <dest> <rval0> <rval1>
            if not isregister(args[0]):
                raise SyntaxError("SUB must sub into register")
            a, b = arg_values(1, 2)
            registers[rnum(args[0])] = a - b

        elif op == STR:  # STR <rval> <loc>
            rval, loc = arg_values(0, 1)
            stack[loc] = rval

        elif op == LDR:  # LDR <dest> <loc>
            if not isregister(args[0]):
                raise SyntaxError("LDR must load into a register")
            dest = rnum(args[0])
            loc = value(args[1])
            registers[dest] = stack[loc]

        elif op == PUT:  # PUT <rval>
            print(value(args[0]), end="")
            sys.stdout.flush()

        elif op == EQ:  # EQ <rval0> <rval1>
            a, b = arg_values(0, 1)
            # Execute the next instruction if a == b
            registers[PC] += 0 if a == b else 1

        elif op == NE:  # NE <rval0> <rval1>
            a, b = arg_values(0, 1)
            # Execute the next instruction if a != b
            registers[PC] += 0 if a != b else 1

        elif op == LT:  # LT <rval0> <rval1>
            a, b = arg_values(0, 1)
            # Execute the next instruction if a < b
            registers[PC] += 0 if a < b else 1

        elif op == GT:  # GT <rval0> <rval1>
            a, b = arg_values(0, 1)
            # Execute the next instruction if a > b
            registers[PC] += 0 if a > b else 1

        elif op == EZ:  # EZ <rval>
            a = value(args[0])
            registers[PC] += 0 if a == 0 else 1
        elif op == NL:
            print()
        registers[PC] += 1
        time.sleep(1.0/HZ)

code, labels = parse(fibo)
run(labels["start"], code)
