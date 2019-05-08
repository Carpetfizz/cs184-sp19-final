import pickle
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('il')
    parser.add_argument('out')
    parser.add_argument('key')

    args = parser.parse_args()

    v = pickle.load(open(args.il, 'rb'))
    d = {}
    d[args.key] = v.tolist()

    with open(args.out,'w') as fp:
    	json.dump(d, fp)

