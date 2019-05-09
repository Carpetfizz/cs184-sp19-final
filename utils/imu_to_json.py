import pandas as pd
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('il')
    parser.add_argument('out')

    ROLL_KEY = "Roll(rads)"
    PITCH_KEY = "Pitch(rads)"
    YAW_KEY = "Yaw(rads)"


    args = parser.parse_args()

    csv_df = pd.DataFrame(pd.read_csv(args.il))

    csv_df = csv_df[[ROLL_KEY, PITCH_KEY, YAW_KEY]]
    r = csv_df.to_numpy()
    d = {}
    d['rotations'] = r.tolist()

    with open(args.out,'w') as fp:
    	json.dump(d, fp)
