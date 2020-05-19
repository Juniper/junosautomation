#!/usr/bin/env python

import json
import yaml
from random import randint


######################################################################

def generate():
    sets = 3
    set_size = 3
    data = {}

    for set in range(sets):
        set_name = 'test' + str(set+1)
        values = []
        for n in range(set_size):
            values.append(randint(1, 100))
        total = sum(values)
        avg = total / len(values)
        data[set_name] = {'values': values,
                          'sum': total,
                          'avg': avg}
    return data


######################################################################

def main():
    data = generate()
    print('Generated data as JSON:')
    print(json.dumps(data, sort_keys=True, indent=4))
    print('=========================')
    print('Generated data as YAML:')
    print(yaml.safe_dump(data, default_flow_style=False))


######################################################################

if __name__ == '__main__':
    main()
