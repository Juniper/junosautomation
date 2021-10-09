import argparse

arguments = {'arg1': 'description1', 'arg2': 'description2'}

def main():
    parser = argparse.ArgumentParser(description='This is a demo script.')

    # Define the arguments accepted by parser
    #  which use the key names defined in the arguments dictionary
    for key in arguments:
        parser.add_argument(('--' + key), required=True, help=arguments[key])
    args = parser.parse_args()

    # Extract the value
    print (args.arg1 + args.arg2)

if __name__ == '__main__':
    main()
