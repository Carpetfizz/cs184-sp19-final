import json
import argparse
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('il')
    parser.add_argument('out')

    args = parser.parse_args()

    path = []

    with open(args.il, 'r') as f:
        d = json.load(f)
        spheres = d['object']['children'][-1]['children']
        for sphere in spheres:
            mtx = sphere['matrix']
            point = [mtx[12], mtx[13], mtx[14]]
            path.append(point)

    
    x = np.array(path)
    plt.plot(x[:,0], x[:,1])
    plt.show()

    j = {'path': path}

    with open(args.out,'w') as fp:
    	json.dump(j, fp)