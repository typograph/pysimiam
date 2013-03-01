import sys

class Struct:
    def __str__(self):
        return "{{{}}}".format(", ".join(["{} : {}".format(k,v) for k,v in self.__dict__.items()]))
        #return str(self.__dict__)

__loaded_modules = set()

def unload_user_modules():
    global __loaded_modules
    while __loaded_modules:
        module = __loaded_modules.pop()
        if module in sys.modules:
            del sys.modules[module]
    for module in list(sys.modules):
        if sys.modules[module] is None:
            del sys.modules[module]
        
def load_by_name(module_string, path = None):
    """Loads a module to the code by name string.
    @params: module_string - module.ModuleName, 
    path - path to module"""
    global __loaded_modules
    try:
        filename, class_name = module_string.split(".")
    except ValueError:
        # either too many or too few dots
        # fallback to capitalization
        filename = module_string.lower()
        class_name = module_string.capitalize()
        
    try:
        if path is not None:
            old_modules = set(sys.modules)
            module = __import__(path, globals(), locals(), [filename]).__dict__[filename]
            __loaded_modules = __loaded_modules.union(set(sys.modules) - old_modules)
        else:
            module = __import__(filename)
            __loaded_modules.add(filename)
        controller_class = module.__dict__[class_name]
        return (module, controller_class)
    except ImportError:
        print "Module {} failed to load".format(filename)
        raise
    except KeyError:
        print "No class {} in module {}".format(class_name,filename)
        raise
