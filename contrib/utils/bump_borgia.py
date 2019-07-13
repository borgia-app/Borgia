"""
Bump Borgia files. It must be executed inside Borgia directory

Use example: python3 ./bump_borgia.py 2019.1.0
"""
import os
import argparse
import json
import fileinput

# Command-line parsing args :
parser = argparse.ArgumentParser(
    description='Bump Borgia files. It must be executed inside Borgia directory. Use example : python3 ./contrib/bump.py 2019.1.0')
parser.add_argument(
    'version', help='The version that need to be written. Ex: 4.7.0')
args = parser.parse_args()


def main():
    """ Main function """
    new_version = str(args.version)
    old_version = get_and_replace_old_version(new_version)
    replace_in_file('README.md', old_version, new_version)
    footer = os.path.join('borgia', 'templates', 'partials', 'footer.html')
    replace_in_file(footer, old_version, new_version)


def get_and_replace_old_version(new_version):
    with open('package.json', 'r') as file:
        json_data = json.load(file)
        old_version = json_data["version"]
    with open('package.json', 'w') as file:
        json_data['version'] = new_version
        json.dump(json_data, file)

    return old_version


def replace_in_file(filename, old_version, new_version):
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            print(line.replace(old_version, new_version), end='')


if __name__ == '__main__':
    main()
