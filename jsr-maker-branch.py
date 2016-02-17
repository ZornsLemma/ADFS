import sys

def strip_comments(line):
    i = line.find(";")
    if i != -1:
        line = line[0:i]
    i = line.find("\\");
    if i != -1:
        line = line[0:i]
    return line.strip()

program = []
sequences = []

def count_sequence_bytes(sequence):
    return sum(operation_bytes(op) for op in sequence)

def operation_bytes(op):
    words = op.split()
    if len(words) == 1:
        return 1 # must be implied
    if words[1][0] == '#':
        return 2 # immediate
    if words[1] == 'A':
        return 1 # implied A (e.g. DEC A)
    i = words[1].find('&')
    if i == -1:
        return 3 # argument is not a literal, so although it's slightly optimistic, it is probably a three byte instruction
    operand = words[1][i+1:]
    value = ''
    for c in operand:
        if c in "0123456789ABCDEFabcdef":
            value += c
        else:
            break
    if len(value)<=2:
        return 2
    else:
        return 3

def sequence_complete(sequence):
    program.append(sequence)

    # Record all possible sub-sequences
    #print "X", sequence
    for new_length in range(1, len(sequence) + 1):
        for i in range(len(sequence) + 1 - new_length):
            sub_sequence = sequence[i:i+new_length]
            sub_sequence_bytes = count_sequence_bytes(sub_sequence)
            #print "Y", sub_sequence, sub_sequence_bytes
            if sub_sequence_bytes > 3:
                # JSR absolute takes 3 bytes, so there's no saving
                # from subroutine-ising short sequences.
                sequences.append((sub_sequence, sub_sequence_bytes))
                # print "Z", sub_sequence, sub_sequence_bytes

def apply_candidate(program_string, candidate_string, candidate_bytes):
    saving = 0
    while candidate_string in program_string:
        saving += candidate_bytes - 3 # 3 bytes for JSR
        i = program_string.find(candidate_string)
        program_string = program_string[i+len(candidate_string):]
    return program_string, saving

def possible_saving(candidate_sequence):
    candidate_instructions, candidate_bytes = candidate_sequence
    candidate_string = ':'.join(candidate_instructions)
    saving = -1 - candidate_bytes # the subroutine-ised copy plus RTS
    for s in program_strings:
        if candidate_string in s:
            modified_s, saved_bytes = apply_candidate(s, candidate_string, candidate_bytes)
            saving += saved_bytes
    #print "ZA",modified_s, saving
    return saving

#program_strings = ["foo:foo:foo", "foo"]
#print possible_saving((["foo"], 5))
#sys.exit(1)

f = open("src/adfs150.asm", "r")
lines = f.readlines()

sequence = []
for l in lines:
    l = strip_comments(l)
    if l == '':
        continue
    j = l.split(':')
    for k in j:
        words = k.split()
        if words[0][0] == '.':
            words = words[1:]
            sequence_complete(sequence)
            sequence = []
        if len(words) == 0:
            continue
        if words[0] in [ 'PHA', 'PHP', 'PHX', 'PHY', 'PLA', 'PLP', 'PLX', 'PLY',
                'RTS', 'TXS', 'TSX', 'IF', 'ELSE', 'ELIF', 'ENDIF', 'EQUB',
                'EQUW', 'EQUS']:
            sequence_complete(sequence)
            sequence = []
            continue
        if words[0] in ['BRA', 'BCC', 'BCS', 'BEQ', 'BNE', 'BPL', 'BMI',
                'BVC','BVS']:
            words = [words[0], "hack"]
        words[0] = words[0].upper()
        thing = ' '.join(words)
        sequence.append(thing)

program_strings = [':'.join(s) for s in program]

print len(sequences)

while True:
    best_saving_sequence = None
    best_saving = 0
    for sequence in sequences:
        saving = possible_saving(sequence)
        if saving > best_saving:
            best_saving = saving
            best_saving_sequence = sequence
    if best_saving == 0:
        break
    print best_saving, best_saving_sequence
    for i in range(len(program_strings)):
        best_saving_string = ':'.join(best_saving_sequence[0])
        if best_saving_string in program_strings[i]:
            modified_program_string, saved_bytes = apply_candidate(program_strings[i], best_saving_string, best_saving_sequence[1])
            program_strings[i] = modified_program_string
            #print "YY",saved_bytes
