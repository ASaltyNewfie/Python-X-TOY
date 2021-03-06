import sys
import re

program_counter = 16 # Equivalent to 'PC' in the TOY Reference Card.
registers = {} # Equivalent to 'R' in the TOY Reference Card.
memory = {} # Equivalent to 'M' in the TOY Reference Card.
debug_mode = False # Output the details of every instruction.


def debug(out):
    if debug_mode: print(out)

# Executes the instruction found at the memory location determined by the
# program counter. Returns True if the program should halt, otherwise False.
def execute():
    global program_counter

    instruction = load_memory(convert_to_hex_string(program_counter))

    # 'opcode', 'd', 's', 't', and 'addr' are the names given by the TOY
    # Reference Card. For consistency, they are also used here.
    opcode = instruction[0]
    d = instruction[1]
    s = instruction[2]
    t = instruction[3]
    addr = instruction[2:4]

    # Instructions 1 through 6 perform math operations on the values found
    # in two registers. For simplicity, those registers are loaded and
    # converted to decimal form.
    a = convert_to_decimal(registers[s])
    b = convert_to_decimal(registers[t])

    # All opcode values are taken from the TOY Reference Card.

    if opcode == '1': # Add
        debug(f'Adding register {s} ({registers[s]}) to register {t} \
                ({registers[t]}) and storing the result in register {d}')
        math_op(d, a + b)
    if opcode == '2': # Subtract
        debug(f'Subtracting register {t} ({registers[t]}) from register {s} \
                ({registers[s]}) and storing the result in register {d}')
        math_op(d, a - b)
    if opcode == '3': # Binary AND
        debug(f'Performing binary AND on registers {s} and {t} and storing \
                the result in register {d}')
        math_op(d, a & b)
    if opcode == '4': # Binary OR
        debug(f'Performing binary OR on registers {s} and {t} and storing the \
                result in register {d}')
        math_op(d, a ^ b)
    if opcode == '5': # Binary left shift
        debug(f'Performing binary left shift on registers {s} by {t} and \
                storing the result in register {d}')
        math_op(d, a << b)
    if opcode == '6': # Binary right shift
        debug(f'Performing binary right shift on registers {s} by {t} and \
                storing the result in register {d}')
        math_op(d, a >> b)

    # Store value 'addr' in register 'd'.
    if opcode == '7':
        debug(f'Storing {addr} in register {d}')
        store_register(d, addr)
    # Store the value found at memory location 'addr' in register 'd',
    if opcode == '8':
        if addr == 'FF':
            debug(f'Storing input in memory {addr}')
            memory[addr] = input(': ')
        debug(f'Storing memory {addr} ({memory[addr]}) in register {d}')
        store_register(d, memory[addr])
    # Store the value in register 'd' in memory location 'addr',
    if opcode == '9':
        if addr == 'FF':
            debug(f'Storing register {d} ({registers[d]}) in memory {addr} \
                    and printing {registers[d]}')
        else:
            debug(f'Storing register {d} ({registers[d]}) in memory {addr}')
        store_memory(addr, registers[d])
    # Store the value found at the memory location defined by the value in
    # register 't', in register 'd' (See TOY Reference Card for a clearer
    # explanation).
    if opcode == 'A':
        if registers[t] == 'FF':
            debug(f'Storing register {d} ({registers[d]}) in memory \
                    {load_memory(registers[t])} and printing {registers[d]}')
        else:
            debug(f'Storing register {d} ({registers[d]}) in memory \
                    {load_memory(registers[t])}')
        store_register(d, load_memory(registers[t]))
    # Store the value found at the memory location defined by the value in
    # register 't', in the memory location defined by the value in register 'd'
    # (See TOY Reference Card for a clearer explanation).
    if opcode == 'B':
        if registers[t] == 'FF':
            debug(f'Storing register {d} ({registers[d]}) in memory \
                    {registers[t]} and printing {registers[d]}')
        else:
            debug(f'Storing register {d} ({registers[d]}) in memory \
                    {registers[t]}')
        store_memory(registers[t], registers[d])

    if opcode == '0': # Halt
        debug('Halting')
        return True
    # If the value in register 'd' == 0, set the program counter to 'addr'.
    if opcode == 'C':
        if convert_to_decimal(registers[d]) == 0:
            debug(f'Checked if register {d} ({registers[d]}) was equal to \
                    zero - it was, so set the program counter to \
                    {convert_to_decimal(addr)}')
            program_counter = convert_to_decimal(addr) - 1
        else:
            debug(f'Checked if register {d} ({registers[d]}) was equal to \
                    zero - it was not')
    # If the value in register 'd' > 0, set the program counter to 'addr'.
    if opcode == 'D':
        if int(registers[d], 16) > 0:
            debug(f'Checked if register {d} ({registers[d]}) was greater than \
                    zero - it was, so set the program counter to \
                    {convert_to_decimal(addr)}')
            program_counter = convert_to_decimal(addr) - 1
        else:
            debug(f'Checked if register {d} ({registers[d]}) was greater than \
                    zero - it was not')
    # Set the program counter to the value in register 'd'.
    if opcode == 'E':
        debug(f'Setting the program counter to register {d} \
                ({convert_to_decimal(registers[d], 16) + 1})')
        program_counter = convert_to_decimal(registers[d], 16)
    # Set the program counter in register 'd', and set the program counter to
    # 'addr'.
    if opcode == 'F':
        print(f'Storing the program counter \
                ({convert_to_hex_string(program_counter)}) in register {d} \
                and setting the program counter to {convert_to_decimal(addr)}')
        store_register(d, convert_to_hex_string(program_counter))
        program_counter = convert_to_decimal(addr) - 1

    program_counter += 1
    return False


# Converts an integer to an 'XX' format where X is a hex digit.
def convert_to_hex_string(i):
    hex_string = hex(i)
    return hex_string[hex_string.find('x') + 1:].upper()


# Accounts for a four-digit hexadecimal two's complement representation.
def convert_to_decimal(x):
    decimal = int(x, 16)
    if decimal > 32767: decimal -= 65536
    return decimal


def load_memory(location):
    # Truncates the argument because it may be longer than necessary.
    return memory[location[-2:]]


def main():
    global debug_mode

    # There are no extra arguments
    if len(sys.argv) == 1:
        file_name = input('File name: ')
    # There is only one extra argumen (a file name to load).
    elif len(sys.argv) >= 2:
        file_name = sys.argv[1]
        # There are two or more extra arguments, if the first of these is '1',
        # activate debug mode.
        if len(sys.argv) >= 3:
            debug_mode = sys.argv[2] == '1'

    with open(file_name, 'r') as f:
        for line in f:
            # Treat any line starting with the patter XX: XXXX as an
            # instruction, where X is a hex digit.
            if re.match(r'^[0-9A-F]{2}: [0-9A-F]{4}', line):
                memory[line[0:2]] = line[4:8]

    while True:
        halt = execute()
        if halt or program_counter > 255: break


# After performing a math operation, check for errors then format and store
# 'value' in register 'destination'.
def math_op(destination, value):
    if value < -32768 or 32767 < value:
        raise Exception(f'Error at {convert_to_hex_string(program_counter)}: \
                          Operation outside the range of -32768 and 32767 \
                          ({str(value)})')
    store_register(destination, convert_to_hex_string(value).zfill(4))


def store_memory(address, value):
    address = str(address).zfill(2)[-2:]
    value = str(value).zfill(4)

    # Output if we are writing to memory location 'FF'.
    if address == 'FF':
        print('> ' + value + ',', convert_to_decimal(value))

    memory[address] = value


def store_register(address, value):
    address = str(address)[-1:]
    value = str(value).zfill(4)
    if address == '00':
        raise Exception(f'Error at {convert_to_hex_string(program_counter)}: \
                          Register 00 is reserved')
    registers[address] = value


if __name__ == '__main__':
    # Initialize registers and memory.
    for i in range(16):
        registers[convert_to_hex_string(i)] = '0000'
    for i in range(256):
        memory[convert_to_hex_string(i).zfill(2)] = '0000'

    main()
