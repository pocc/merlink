'''Create a .zip like a not-terrible person.'''
import os
import sys
import zipfile

def create_zip(zip_name, *dir_names, suffix='.zip'):
    '''Create archive from directories (but paths prefixed by $prefix)'''
    prefix = zip_name[:-len(suffix)] if zip_name.endswith(suffix) else zip_name
    with zipfile.ZipFile(prefix + suffix, 'w') as zip_file:
        for dir_name in dir_names:
            for dir_path, _, file_names in os.walk(dir_name):
                for file_name in file_names:
                    is_pycache = '__pycache__' in dir_path
                    is_pyc = file_name.endswith('.pyc')
                    if not (is_pyc or is_pycache):
                        source = '%s/%s' % (dir_path, file_name)
                        target = '%s/%s' % (prefix, source)
                        zip_file.write(source, target)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        USAGE = 'USAGE: python3 ./%s name[.zip] ...files'
        print(USAGE % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    else:
        create_zip(sys.argv[1], *sys.argv[2:])
        sys.exit(0)
