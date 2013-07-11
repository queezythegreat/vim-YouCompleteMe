# This file is NOT licensed under the GPLv3, which is the license for the rest
# of YouCompleteMe.
#
# Here's the license text for this file:
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import os
import glob
import inspect
import ycm_core



LANGUAGES = {
    'c': [
        'c90',              # Support all ISO C90 programs (certain GNU extensions
        'c89',              #  that conflict with ISO C90 are disabled). Same as -ansi for C code.
        'iso9899:1990',

        'iso9899:199409',   # ISO C90 as modified in amendment 1.

        'c99',              # ISO C99.  Note that this standard is not yet fully supported;
        'c9x',              #  see <http://gcc.gnu.org/gcc-4.7/c99status.html> for more information.
        'iso9899:1999',     #  The names c9x and iso9899:199x are deprecated.
        'iso9899:199x',

        'c11',              # ISO C11, the 2011 revision of the ISO C standard.
        'c1x',              #  Support is incomplete and experimental.  The name c1x is deprecated.
        'iso9899:2011',

        'gnu90',            # GNU dialect of ISO C90 (including some C99 features). This is the default for C code.
        'gnu89',            # 

        'gnu99',            # GNU dialect of ISO C99.  When ISO C99 is fully implemented in GCC,
        'gnu9x',            #  this will become the default.  The name gnu9x is deprecated.

        'gnu11',            # GNU dialect of ISO C11.  Support is incomplete and experimental.
        'gnu1x',            #  The name gnu1x is deprecated.
        ],
    'c++': [
        'c++98',            # The 1998 ISO C++ standard plus amendments. Same as -ansi for C++ code.

        'gnu++98',          # GNU dialect of -std=c++98.  This is the default for C++ code.
        
        'c++11',            # The 2011 ISO C++ standard plus amendments.
                            #  Support for C++11 is still experimental, and may change in incompatible
                            #  ways in future releases.
        
        'gnu++11',          # GNU dialect of -std=c++11. Support for C++11 is still experimental, and may
                            #  change in incompatible ways in future releases.
        ],
    'objective-c':   [],
    'objective-c++': [],
    }

LANGUAGE_DEFAULTS = {
    'c':   'gnu90',
    'c++': 'gnu++98',
}

LANGUAGE_EXTENSIONS = {
    'c':   ['c', 'h'],
    'c++': ['cpp', 'cc', 'c++', 'hpp', 'hxx', 'tcc', 'txx'],
}

def script_abspath(filepath=__file__):
    """ Return absolute path of this python module. """
    return os.path.dirname(os.path.abspath(filepath))


def abspath_flags(flags, working_directory):
    """ Convert compiler flags to use absolute paths. """
    if not working_directory:
        return list(flags)
    new_flags = []
    make_next_absolute = False
    path_flags = [ '-isystem', '-I', '-iquote', '--sysroot=' ]
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith( '/' ):
                new_flag = os.path.abspath(os.path.join( working_directory, flag ))

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith( path_flag ):
                path = flag[ len( path_flag ): ]
                new_flag = path_flag + os.path.join( working_directory, path )
                break

        if new_flag:
            new_flags.append( new_flag )
    return new_flags

def load_database(database_path):
    """ Load compilation database (LLVM compile_commands.json). """
    if database_path:
        return ycm_core.CompilationDatabase(database_path)

def load_database_flags(database, filename): 
    """ Loadd compilation flags from compiler database (compile_commands.json). """
    if database:
        # Bear in mind that compilation_info.compiler_flags_ does NOT return a
        # python list, but a "list-like" StringVec object
        compiler_info = database.GetCompilationInfoForFile(filename)
        final_flags = abspath_flags(compiler_info.compiler_flags_,
                                    compiler_info.compiler_working_dir_ )
        return final_flags

def load_user_flags(flags, include_dirs, include_system_dirs, config_path):
    """ Load user compiler flags.

        flags               - list of flags
        include_dirs        - list of include directories (-I)
        include_system_dirs - list of system include directories (-isystem)
        config_path         - YCM configuration file path
    """

    for path in include_dirs:
        flags += ['-I', path] 

    for path in include_system_dirs:
        flags += ['-isystem', path] 
    
    return abspath_flags(flags, script_abspath(config_path))

def load_language_flags(language, standard):
    """ Load flags specifying the compiler language and standard. """
    flags = []
    if language in LANGUAGES:
        flags += ['-x', language]

        if standard in LANGUAGES[language]:
            flags += ['-std=%s' % standard]
        elif language in LANGUAGE_DEFAULTS:
            flags += ['-std=%s' % LANGUAGE_DEFAULTS[language]]

    return flags

def glob_dirs(path_globs):
    all_paths = []
    for path_glob in path_globs:
        all_paths += [p for p in glob.glob(path_glob) if os.path.isdir(p)]
    return all_paths

def caller_scope():
    """ Get function caller environment locals. """
    stack = inspect.stack()
    try:
        return stack[2][0].f_locals
    finally:
        del stack

def flags_loader(*args, **kwargs):
    caller = caller_scope()

    database = caller.get('DATABASE', DATABASE)
    flags = caller.get('FLAGS', FLAGS)
    include_dirs = caller.get('INCLUDE_DIRS', INCLUDE_DIRS)
    include_system_dirs = caller.get('INCLUDE_SYSTEM_DIRS', INCLUDE_SYSTEM_DIRS)

    language = caller.get('LANGUAGE', LANGUAGE)
    language_standard = caller.get('LANGUAGE_STANDARD', LANGUAGE_STANDARD)
    enable_cache = caller.get('ENABLE_CACHE', ENABLE_CACHE)
    config_path = caller.get('__file__', __file__)

    include_dirs = glob_dirs(include_dirs)
    include_system_dirs = glob_dirs(include_system_dirs)
    def decorator(func):
        def load_flags(filename):
            """ Load flags for given file. """
            all_flags = load_database_flags(database, filename)

            if not all_flags:
                all_flags = load_user_flags(flags, include_dirs, include_system_dirs, config_path)
                all_flags += load_language_flags(language, language_standard)

            result = {
                    'flags': all_flags,
                    'do_cache': enable_cache
                    }
            return func(filename, result)
        return load_flags
    return decorator




# Compiler Flags
FLAGS = [
    '-Wall',
    '-Wextra',
#    '-Werror',
    '-Wc++98-compat',
    '-Wno-long-long',
    '-Wno-variadic-macros',
    '-fexceptions',
]


# Load LLVM compiler_commands.json database (path to directory)
DATABASE = load_database('')

# Language and optional language standard (eg. language C and standard C99)
LANGUAGE = 'c++'
LANGUAGE_STANDARD = ''

# List of include directories
# Relative paths from this file, uses the `-I` compiler flag
INCLUDE_DIRS = [
    os.path.abspath('.'),
]

ENABLE_CACHE = True

# List of system include directories (warning get ignored)
# Relative paths from this file, uses the `-isystem` compiler flag
INCLUDE_SYSTEM_DIRS = [
    '/usr/include',
]


@flags_loader()
def FlagsForFile(filename, result, *kwargs):
    # Custom flag handling here...
    return result
