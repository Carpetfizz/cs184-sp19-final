import pickle
import json
import argparse
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('il')
    parser.add_argument('out')
    parser.add_argument('key')

    args = parser.parse_args()

    v = pickle.load(open(args.il, 'rb'))

    l = []

    for i in range(np.size(v, 0)):
        point = v[i, :]
        l.append([point[0], 0, point[1]])

    d = {}
    d[args.key] = l

    with open(args.out,'w') as fp:
    	json.dump(d, fp)

