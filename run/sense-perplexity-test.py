from nlp_utils import evaluate_mean_average_perp_diff


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--key-file', required=True)
    parser.add_argument('--system-file', required=True)
    args = parser.parse_args()
    print evaluate_mean_average_perp_diff(args.key_file, args.system_file)


if __name__ == '__main__':
    main()

# python sense-perplexity-test.py --key-file s13-test.key --system-file system100.ans
