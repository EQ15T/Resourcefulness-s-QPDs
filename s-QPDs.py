import re
import numpy as np

### Reading the bosonic circuit
_REAL = r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
_NAT = r'(?:[1-9]\d*)'
_RE_S = re.compile(rf'S([+-]?{_REAL}),({_NAT})')
_RE_R = re.compile(rf'R([+-]?{_REAL}),({_NAT})')
_RE_C = re.compile(rf'C([+-]?{_REAL}),({_NAT})')   # C: real, nat
_RE_L = re.compile(rf'L([+-]?{_REAL}),({_NAT})')   # L: real, nat
_RE_B = re.compile(rf'B([+-]?{_REAL}),({_NAT}),({_NAT})')

def _to_real(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Invalid real number: '{s}'")

def _to_nat(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise ValueError(f"Invalid natural number: '{s}'")
    if v < 1:
        raise ValueError(f"Natural number must be >= 1, got {v}")
    return v

def parse_input(input_str: str):
    s = input_str.strip()
    if any(ch.isspace() for ch in s):
        i = next(i for i, ch in enumerate(s) if ch.isspace())
        snippet = s[max(0, i-5):i+5]
        raise ValueError(f"Spaces are not allowed (first space at position {i}): '{snippet}'")
    pos = 0
    n = len(s)
    data = {'S': [], 'R': [], 'C': [], 'L': [], 'B': []}
    x = []
    while pos < n:
        matched = False
        for kind, regex in (('S', _RE_S), ('R', _RE_R), ('C', _RE_C), ('L', _RE_L), ('B', _RE_B)):
            m = regex.match(s, pos)
            if not m:
                continue
            if kind in ('S', 'R', 'C', 'L'):
                real_str, nat_str = m.group(1), m.group(2)
                val1 = _to_real(real_str)
                val2 = _to_nat(nat_str)
                data[kind].append((val1, val2))
                x.append((kind, val1, val2))
            else:  # 'B'
                real_str, nat1_str, nat2_str = m.group(1), m.group(2), m.group(3)
                val1 = _to_real(real_str)
                val2 = _to_nat(nat1_str)
                val3 = _to_nat(nat2_str)
                data['B'].append((val1, val2, val3))
                x.append(('B', val1, val2, val3))
            pos = m.end()
            matched = True
            break
        if not matched:
            snippet = s[pos:pos+12]
            raise ValueError(
                f"Invalid token starting at position {pos}: '{snippet}'. "
                "Expected one of:\n"
                "  S<real>,<nat>\n"
                "  R<real>,<nat>\n"
                "  C<real>,<nat>\n"
                "  L<real>,<nat>\n"
                "  B<real>,<nat>,<nat>\n"
                "Numbers must be comma-separated, with no spaces."
            )
    return data, x

# Gate fonctions
def s_losses(s_in, eta):
    """Return the best output ordering parameter for the Losses given s_in, and some losses eta"""
    return float(1 - eta * (1 - s_in))

def s_squeezing(s_in, r):
    """Return the best output ordering parameter for the Squeezing gate given s_in, and a squeezing parameter r"""
    if s_in >= 0:
        return float(s_in / np.exp(2 * np.abs(r)))
    else:
        return float(s_in / np.exp(-2 * np.abs(r)))

def s_beamsplitter(s_in1, s_in2, theta):
    """Return the best output ordering parameter for the Beam-splitter given s_in, and the BS angle theta"""
    return float(min(s_in1, s_in2))

def s_cubic(s_in, gamma):
    """Return the best output ordering parameter for the Cubic phase gate given s_in, and the cubicity gamma"""
    if s_in ==1 : 
        return -1 #In the case of a 
    else:
        return -100 #

# Process 
def process_list(s_in, circuit):
    """Process the list of quantum of operations to find the optimal ordering parameters."""
    data, x = parse_input(circuit)
    for index, item in enumerate(x):
        if item[0] == 'S':
            s_in[item[2]] = s_squeezing(s_in[item[2]], item[1])
            if not (-1 <= s_in[item[2]] <= 1):
                raise ValueError(f"The value of the ordering parameter s is outside [-1,1] after the application of gate 'S' on mode {item[2]} (gate number {index}). At this step, s={s_in}. A positive decomposition cannot be found this way.")
        elif item[0] == 'L':
            s_in[item[2]] = s_losses(s_in[item[2]], item[1])
            if not (-1 <= s_in[item[2]] <= 1):
                raise ValueError(f"The value of the ordering parameter s is outside [-1,1] after the application of gate 'L' on mode {item[2]} (gate number {index}). At this step, s={s_in}. A positive decomposition cannot be found this way.")
        elif item[0] == 'C':
            result = s_cubic(s_in[item[2]], item[1])
            if result is not None:
                s_in[item[2]] = result
                if not (-1 <= s_in[item[2]] <= 1):
                    raise ValueError(f"The value of the ordering parameter s is outside [-1,1] after the application of gate 'C' on mode {item[2]} (gate number {index}). At this step, s={s_in}. A positive decomposition cannot be found this way.")
        elif item[0] == 'B':
            s_in[item[2]] = s_beamsplitter(s_in[item[2]], s_in[item[3]], item[1])
            s_in[item[3]] = s_beamsplitter(s_in[item[2]], s_in[item[3]], item[1])
            if not (-1 <= s_in[item[2]] <= 1) or not (-1 <= s_in[item[3]] <= 1):
                raise ValueError(f"The value of the ordering parameter s is outside [-1,1] after the application of gate 'BS' on mode {item[2]} (gate number {index}). At this step, s={s_in}. A positive decomposition cannot be found this way.")
        elif item[0] == 'R':
            pass
    return s_in


# Ask the user to input the initial ordering parameters
while True:
    s_in_input = input("Please input the best ordering parameter for your input state, each mode separated by a comma : ")
    if not s_in_input:
        print("Error: Please input at least one value.")
        continue
    try:
        s_in = [float(x) for x in s_in_input.split(',')]
        # Check that all values are between -1 and 1
        invalid_values = [x for x in s_in if not (-1 <= x <= 1)]
        if invalid_values:
            print(f"Error: The inputs must be between -1 and 1: {invalid_values}")
        else:
            break
    except ValueError:
        print("Error: Please input valid numbers separated by commas.")

# Display the number of modes
print(f"The number of modes is {len(s_in)}")

# Define the circuit to process
test = 'S1.2,3R-0.5,2C0.0,4L3,1B-2.5,2,5'
try:
    result = process_list(s_in, test)
    print("After the quantum process, the best ordering parameters are:", result)
except ValueError as e:
    print(e)

# Ask the user to input their own parameters (non-classical depth)
while True:
    user_params_input = input("Please input the non-classical depth parameters for your measurement, each mode separated by a comma : ")
    if not user_params_input:
        print("Error: Please input at least one value.")
        continue
    try:
        user_params = [float(x) for x in user_params_input.split(',')]
        if len(user_params) != len(result):
            print(f"Error: The number of parameters must be equal to the number of modes, i.e. {len(result)}.")
        else:
            break
    except ValueError:
        print("Error: Please input valid numbers separated by commas.")

# Compare the user's parameters with the result
all_less = True
for i, (user_param, result_param) in enumerate(zip(user_params, result)):
    if user_param >= result_param:
        all_less = False
        break

if all_less:
    print("It is possible to simulate your process classically.")
else:
    print("It is not possible to simulate your process classically with the provided parameters using this method.")