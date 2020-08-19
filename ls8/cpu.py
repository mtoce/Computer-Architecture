"""CPU functionality."""

import sys

# instruction codes
HLT = 0b00000001 # halt
LDI = 0b10000010 # sets a specified register to a value
PRN = 0b01000111 # print
ADD = 0b10100000 # add
SUB = 0b10100001 # subtract
MUL = 0b10100010 # multiply
INC = 0b01100101 # increment
DEC = 0b01100110 # decrement
PUSH = 0b01000101 # push
POP = 0b01000110 # pop

# Variables for bitwise AND operations
OOI = 0b00000111 # prevent out of index
LIM = 0b11111111 # limit values

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

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
        else:
            raise Exception("Unsupported ALU operation")

    def ldi(self, reg, val):
        reg = reg & OOI # bitwise AND to prevent out-of-index
        val = val & LIM # bitwise AND to limit values
        self.reg[reg] = val

    def push(self, reg):
        # decrement value in register 7 (stack pointer)
        self.alu(DEC, 7, 0)
        # filter incoming register value and write to RAM
        reg = reg & OOI
        # write value in reg a in RAM at address given by
        # stack pointer (register 7)
        self.ram_write(self.reg[reg], self.reg[7])

    def pop(self, reg):
        # filter incoming register value and read from
        # the address stored in that address
        reg = reg & OOI
        # read value in RAM at address given by stack pointer
        # store in reg a
        mem_data_reg = self.ram_read(self.reg[7])
        self.ldi(reg, mem_data_reg)
        # increment the stack pointer
        self.alu(INC, 7, 0)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
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
            instruction_register = self.ram_read(self.pc)
            
            # in case the instructions need them
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # perform the actions needed for instruction per the LS-8 spec
            if instruction_register == HLT:     # HALT
                self.running = False
            elif instruction_register == LDI:   # LOAD IMMEDIATE
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction_register == PRN:   # PRINT
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction_register == ADD:   # ADD
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == SUB:   # SUBTRACT
                self.alu("SUB", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == MUL:   # MULTIPLY
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == PUSH:  # PUSH
                self.push(operand_a)
            elif instruction_register == POP:   # POP
                self.pop(operand_a)
            else:
                print("Instruction not valid")
