"""CPU functionality."""

import sys

# instruction codes
HLT = 0b00000001    # halt
LDI = 0b10000010    # sets a specified register to a value
PRN = 0b01000111    # print
ADD = 0b10100000    # add
SUB = 0b10100001    # subtract
MUL = 0b10100010    # multiply
INC = 0b01100101    # increment
DEC = 0b01100110    # decrement
PUSH = 0b01000101   # push onto stack
POP = 0b01000110    # pop off the stack
CALL = 0b01010000   # call
RET = 0b00010001    # return
CMP = 0b10100111    # compare
JMP = 0b01010100    # jump
JEQ = 0b01010101    # equal
JNE = 0b01010110    # not equal
OOI = 0b00000111    # prevent out of index
LIM = 0b11111111    # limit values


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # ram holds 256 bytes of memory
        self.ram = [0] * 256
        # holding 8 general-purpose registers
        self.reg = [0] * 8
        # program counter (pc)
        self.pc = 0
        # stack pointer (sp)
        self.sp = 7
        # CPU running
        self.running = True
        # create branchtable
        self.branchtable = {
            HLT: self.halt,
            LDI: self.ldi,
            PRN: self.print,
            ADD: self.add,
            SUB: self.subtract,
            MUL: self.multiply,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self._return,
            CMP: self.compare,
            JEQ: self.jump_if_equal,
            JNE: self.jump_if_not_equal,
            JMP: self.jump
        }

    def ram_read(self, address):
        # return the ram at the specified, indexed address
        return self.ram[address]

    # defining a function to overwrite the ram value at the given address
    def ram_write(self, value, address):
        # set the ram at the specified, indexed address, as the value
        self.ram[address] = value

    def load(self, filename=None):
        """Load a program into memory."""

        address = 0

        # if cpu not being fed 2 files (file_to_run, file_to_load)
        if len(sys.argv) != 2:
            print("Usage: cpu.py loaded_program_name.ls8")

        # open the file
        try:    # catch FileNotFound errors
            with open(filename, 'r') as f:
                for line in f:
                    # only take code to the left of any comments
                    line = line.split("#")[0].strip()
                    # Skip past empty lines and commented lines
                    if line == '' or line[0][0] == '#':
                        continue
                    # Since we're working in binary, have to set base to 2
                    try:
                        self.ram[address] = int(line, 2)
                    # Raise error if not fed appropriate int
                    except ValueError:
                        print(f'Invalid number: {line}')
                        sys.exit(1)
                    address += 1
        except FileNotFoundError:
            print(f"Could not find file: {sys.argv[1]}")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        reg_a = reg_a & OOI
        reg_b = reg_b & OOI
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "INC":  # INC
            self.reg[reg_a] += 1
            self.reg[reg_a] = self.reg[reg_a] & LIM
        elif op == "DEC":   # DEC
            self.reg[reg_a] -= 1
            self.reg[reg_a] = self.reg[reg_a] & LIM
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = HLT
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def ldi(self, operand_a, operand_b):
        operand_a = operand_a & OOI  # bitwise AND to prevent out-of-index
        operand_b = operand_b & LIM  # bitwise AND to limit values
        # IR = self.ram_read(self.pc)
        self.reg[operand_a] = operand_b
        # self.reg[operand_a] = operand_b
        self.pc += 3

    def print(self, operand_a, operand_b=None):
        print(self.reg[operand_a])
        self.pc += 2

    def halt(self, operand_a=None, operand_b=None):
        self.running = False

    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def subtract(self, operand_a, operand_b):
        self.alu("SUB", operand_a, operand_b)
        self.pc += 3

    def multiply(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def compare(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def jump(self, operand_a, operand_b=None):
        self.pc = self.reg[operand_a]

    def jump_if_equal(self, operand_a, operand_b=None):
        if self.flag == HLT:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jump_if_not_equal(self, operand_a, operand_b=None):
        if self.flag != HLT:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def push(self, operand_a, operand_b=None):
        # decrement the stack pointer
        self.reg[self.sp] -= 1
        # store the value at that address
        self.ram_write(self.reg[operand_a], self.reg[self.sp])
        # increment the program counter
        self.pc += 2

    def pop(self, operand_a, operand_b=None):
        # take the value that is stored at the top of the stack
        self.reg[operand_a] = self.ram_read(self.reg[self.sp])
        # increment the stack pointer
        self.reg[self.sp] += 1
        # increment the program counter
        self.pc += 2

    def call(self, operand_a, operand_b=None):
        # decrement the stack pointer
        self.reg[self.sp] -= 1
        # push the address of the instruction after it onto the stack
        self.ram_write(self.pc + 2, self.reg[self.sp])
        # move the program counter to the subroutine address
        self.pc = self.reg[operand_a]

    def _return(self, operand_a=None, operand_b=None):
        # pop the addr off the stack and store it in the prog counter
        self.pc = self.ram_read(self.reg[self.sp])
        # increment the stack pointer
        self.reg[self.sp] += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            # self.trace()

            # instruction register
            IR = self.ram_read(self.pc)

            # in case the instructions need them
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[IR](operand_a, operand_b)
