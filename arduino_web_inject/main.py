##
# Arduino Web Inject
#
# Inject and build web files into your sketches.
#
# Copyright (c) 2020 Francesco Bianco <bianco@javanile.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##

import asyncio
import glob
import re 
import os
import sys

from watchfiles import awatch
from csscompressor import compress
from jsmin import jsmin
from htmlmin import minify 
from binaryornot.check import is_binary

__version__ = '0.1.27'

watch_dir = os.getcwd()
watch_ext = ('.ino', '.cpp', '.h', '.c')

ignore_ext = ('.lock')

def get_files(dir):
    files = []
    for ext in watch_ext:
        pattern = dir + '/**/*' + ext
        files.extend(glob.glob(pattern, recursive=True))
    return files

def stringify(code):
    code = re.sub(r'"', r'\"', code)
    code = re.sub(r'\{\{[ \t]*([a-zA-Z_][a-zA-Z0-9_]+)[ \t]*\}\}', r'" + \g<1> + "', code)
    return '"' + code + '"'

def inject(dir, parsed_file, changed_file):
    #print("-- "+parsed_file+" - "+changed_file)
    def replace(lines):
        old_code = lines.group(0)
        inject_file = os.path.dirname(parsed_file) + "/" +lines.group(2)
        inject_type = re.split(r'\W+', lines.group(3))        
        if not os.path.exists(inject_file):
            return lines.group(1) + ' ' + '"File not found: ' + inject_file + '";'
        else:
            inject_file = os.path.abspath(inject_file);
            if (parsed_file == changed_file) or (inject_file == changed_file):
                if "String" not in inject_type or is_binary(inject_file):
                    code = inject_as_binary(inject_file, old_code)
                else:
                    code = inject_as_string(inject_file, old_code)
                new_code = lines.group(1) + ' ' + code + ';'        
                if new_code != old_code:
                    log_inject(dir, inject_file)                    
                return new_code
        return old_code                            
    return replace

def inject_as_binary(file, code):
    with open(file, "rb") as f:
        bytes = []
        byte = f.read(1)
        while byte != b"":
            bytes.append(f'0x{ord(byte):02x}')
            byte = f.read(1)
        code = '{' + ', '.join(bytes) + '}'
    return code

def inject_as_string(file, code):
    with open(file, "r") as f:
        code = f.read()
        if file.lower().endswith('.js'):
            code = jsmin(code)
        elif file.lower().endswith('.css'):
            code = compress(code)
        elif file.lower().endswith('.html'):
            code = minify(code, remove_comments=True, remove_empty_space=True)
        code = stringify(code);
    return code

def log_update(dir, file):
    print('Update: ' + os.path.relpath(file, dir))

def log_inject(dir, file):
    print('Inject: ' + os.path.relpath(file, dir))

def parse(dir, parsed_file, changed_file):
    pattern = r'(// @inject "([A-Za-z0-9./-_]+)"[\t ]*[\n][\t ]*([A-Za-z0-9 ]+) ([A-Za-z0-9_]+)(\[\])? =)(.*);'
    with open(parsed_file, "r") as f:
        source = f.read()                   
        change = re.sub(pattern, inject(dir, parsed_file, changed_file), source, flags = re.MULTILINE)
        if source != change:
            log_update(dir, parsed_file)            
            with open(parsed_file, "w") as f: f.write(change)
            with open(parsed_file + '.lock', 'a'): pass
    
def build(dir, changed_file):
    all_files = get_files(dir)
    if changed_file in all_files:
        parse(dir, changed_file, changed_file)
    else:
        for file in all_files:
            parsed_file = os.path.abspath(file)
            parse(dir, parsed_file, changed_file)
        
async def watch(dir):
    try: 
        async for changes in awatch(dir):        
            for val in changes:
                file = val[1];
                if file.lower().endswith(ignore_ext):
                    continue
                elif os.path.exists(file + '.lock'):
                    os.remove(file + '.lock')
                else:                        
                    #print("Change: " + file);            
                    build(dir, file)
    except RuntimeError:
        print("heers^")

def main():
    if sys.argv[1]:
        watch_dir = sys.argv[1]
    if not os.path.isdir(watch_dir):
        print("Your input is not a directory: " + watch_dir)
    else:
        print("Watching for changes on: " + watch_dir + "\n")
        watch_dir = os.path.abspath(watch_dir)
        try:        
            asyncio.run(watch(watch_dir))
        except KeyboardInterrupt:            
            sys.exit()
    
if __name__ == '__main__':
    main()
