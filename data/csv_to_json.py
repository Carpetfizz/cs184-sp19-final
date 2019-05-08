import pandas as pd
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('il')
    parser.add_argument('out')

    args = parser.parse_args()

    csv_file = pd.DataFrame(pd.read_csv(args.il))
    csv_file.to_json(args.out)
