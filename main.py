import sys
import re
import string


data = {'var': dict.fromkeys(string.ascii_uppercase, 0), 'rules': {}, 'request': [], 'result': {}}
operation = ['(', ')', '!', '+', '|', '^']


def error(line):
    raise ValueError(line)


def check_order(line, i):
    for c in line:
        if c == '!' or c == '(':
            if i % 2 == 1:
                error("Invalid order: '{}'".format(" ".join(line)))
            continue
        if c == ')':
            if i % 2 == 0:
                error("Invalid order: '{}'".format(" ".join(line)))
            continue
        if i % 2 == 0 and c not in data['var']:
            error("Invalid order: '{}'".format(" ".join(line)))
        i += 1
    if i % 2 == 0:
        error("Invalid order: '{}'".format(" ".join(line)))


def syntax_check_left(line, i):
    for c in line:
        if c not in operation and c not in data['var']:
            error("Invalid value: '{}'".format(" ".join(line)))
        if c == '(':
            i += 1
        elif c == ')':
            i -= 1
            if i < 0:
                error("Invalid parentheses: '{}'!".format(" ".join(line)))
    if i != 0:
        error("Invalid parentheses: '{}'!".format(" ".join(line)))
    check_order(line, 0)


def syntax_check_right(line, i):
    for c in line:
        if c not in operation and c not in data['var']:
            error("Invalid value: '{}'".format(" ".join(line)))
        if c == '(':
            i += 1
        elif c == ')':
            i -= 1
            if i < 0:
                error("Invalid parentheses: '{}'!".format(" ".join(line)))
    if i != 0:
        error("Invalid parentheses: '{}'!".format(" ".join(line)))
    check_order(line, 0)


def get_true(line):
    for c in re.findall(r'.', line.replace('=', '', 1).replace(' ', '')):
        if c not in data['var']:
            error("Non found key: '{}'!".format(c))
        data['var'][c] = 1


def get_request(line):
    for c in re.findall(r'.', line.replace('?', '', 1).replace(' ', '')):
        if c not in data['var']:
            error("Non found key: '{}'!".format(c))
        data['request'].append(c)


def add_rule(line):
    left = "".join(re.split('=>', line)[0].split())
    syntax_check_left(left, 0)
    right = "".join(re.split('=>', line)[1].split())
    syntax_check_right(right, 0)
    data['rules'][left] = right


def handle_input(f):
    for line in f:
        if '#' in line:
            line = re.split('#', line)[0]
        line = line.lstrip()
        if line == '\n' or line == '':
            continue
        if re.match('=', line):
            get_true(line)
        elif re.match(r'\?', line):
            get_request(line)
        elif '=>' in line:
            add_rule(line)
        else:
            error("Invalid line: '{}'!".format(line.replace('\n', '')))


def right_side(rule, one, result):
    if count_expression(re.sub(one, '1', rule), rule) == result and\
            count_expression(re.sub(one, '0', rule), rule) == result:
        return 2
    if count_expression(re.sub(one, '1', rule), rule) != result and\
            count_expression(re.sub(one, '0', rule), rule) != result:
        return -1
    elif count_expression(re.sub(one, '1', rule), rule) == result:
        return 1
    else:
        return 0


def inv(q):
    return int(not q)


def count_expression(line, rule):
    for i in range(0, len(line)):
        if line[i] in data['var']:
            if data['var'][line[i]]:
                buff = 1
            else:
                buff = count_one(line[i], rule)
            line = line.replace(line[i], str(int(buff)), 1)
        if line[i] is '+':
            line = line.replace(line[i], '&', 1)
    while '!' in line:
        for i in range(0, len(line)):
            if line[i] == '!' and line[i + 1] != '(':
                line = line[:i] + ' inv(' + line[i + 1] + ') ' + line[i + 2:]
            if line[i] == '!' and line[i + 1] == '(':
                j = line.find(')', i + 1)
                line = line[:i] + ' inv(' + line[i+2:j] + ') ' + line[j+1:]

    return eval(line)


def count_one(one, inf_rule):
    if data['var'][one]:
        return 1
    for rule in data['rules']:
        if one in inf_rule:
            continue
        if one in rule and one in data['rules'][rule]:
            error("Endless loop: '{}'".format(rule))
        if one in data['rules'][rule]:
            if count_expression(rule, data['rules'][rule]) == -1:
                return -1
            if count_expression(rule, data['rules'][rule]):
                return right_side(data['rules'][rule], one, 1)
    for rule in data['rules']:
        if one in inf_rule:
            continue
        if one in data['rules'][rule]:
            if right_side(data['rules'][rule], one, 0) != 0:
                return right_side(data['rules'][rule], one, 0)
    return 0


def count(all_var):
    for one in all_var:
        data['result'][one] = count_one(one, '')


def output():
    for result in sorted(data['result']):
        if data['result'][result] == 0:
            print('\033[91m' + result + ': False\033[0m')
        if data['result'][result] == 1:
            print('\033[92m' + result + ': True\033[0m')
        if data['result'][result] == 2:
            print('\033[93m' + result + ': Undetermined\033[0m')
        if data['result'][result] == -1:
            print('\033[94m' + result + ': Impossible\033[0m')
    print()


def main(argv):
    for i in range(1, len(argv)):
        try:
            f = open(argv[i])
        except IOError:
            print('\033[95m------- ' + argv[i] + ' -------\033[0m')
            print('Invalid file: {}!\n'.format(argv[i]))
            continue
        print('\033[95m------- ' + argv[i] + ' -------\033[0m')
        try:
            handle_input(f)
            count(data['request'])
            output()
            f.close()
        except ValueError as exc:
            print('\033[91m' + str(exc) + '\033[0m\n')


try:
    main(sys.argv)
except Exception as ex:
    print(ex)
