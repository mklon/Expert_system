from func import *

try:
    f = open(sys.argv[1])
except IOError:
    print('Invalid file: {}!'.format(sys.argv[1]))
    sys.exit(1)

handle_input(f)
count(data['request'])
pprint.pprint(data['result'])



