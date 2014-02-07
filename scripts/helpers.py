import sys
import json

class Struct:
    """This class describes structures with arbitrary fields.
       It is used, e.g. for the communication between the supervisor and the UI.
       
       Example::
       
            p = Struct()
            p.goal = Struct()
            p.goal.x = 0.0
            p.goal.y = 0.5
            p.velocity = Struct()
            p.velocity.v = 0.2
            p.gains = Struct()
            p.gains.kp = 10.0
            p.gains.ki = 2.0
            p.gains.kd = 0.0
            
       Alternatives::
       
            p = Struct({'goal':{'x':0.0, 'y':0.5}, 'velocity':{'v':0.2}, 'gains':{'kp':10.0, 'ki':2.0, 'kd':0.0}})
            p = Struct("{'goal':{'x':0.0, 'y':0.5}, 'velocity':{'v':0.2}, 'gains':{'kp':10.0, 'ki':2.0, 'kd':0.0}}")
           
       In the second case, the string has to be a valid JSON object. It is also impossible to use dictionaries as
       values in the Struct in these cases.
                   
    """
    def __init__(self,desc = None):
        if desc is not None:
            try:
                dct = dict(desc)
            except Exception:
                try:
                    dct = dict(json.loads(desc))
                except Exception:
                    raise ValueError("Invalid Struct description {}".format(repr(desc)))
            
            for k,v in dct.items():
                if isinstance(v,dict):
                    self.__dict__[k] = Struct(v)
                else:
                    self.__dict__[k] = v
    
    def __str__(self):
        def str_field(key,value):
            indent = " "*(len(str(key)) + 3)
            str_value = str(value)
            if isinstance(value,Struct):
                # create indent
                str_value = str_value.replace('\n','\n'+indent)
            return "{}: {}".format(key,str_value)
        
        
        return "Struct\n {}".format("\n ".join((str_field(k,v) for k,v in self.__dict__.items())))
    
    def __repr__(self):
        return json.dumps(self.__dict__) # This might be the same as repr(dict), but it's safer.
    
    def __eq__(self,other):
        if not isinstance(other,Struct):
            return NotImplemented
        
        return len(self.__dict__) == len(other.__dict__) and all(k in other.__dict__ and other.__dict__[k] == v  for k,v in self.__dict__.items() )  

__loaded_modules = set()

def unload_user_modules():
    """Unload all modules loaded so far with :func:`~helpers.load_by_name`"""
    global __loaded_modules
    if 'helpers' in __loaded_modules:
        __loaded_modules.remove('helpers')
    while __loaded_modules:
        module = __loaded_modules.pop()
        if module in sys.modules:
            del sys.modules[module]
    for module in list(sys.modules):
        if sys.modules[module] is None:
            del sys.modules[module]
        
def load_by_name(module_string, path = None):
    """Load a class from a module, specified by *module_string*.
    
       The *path* is an additional path that is prepended to the module string.
       
       E.g. ``C = load_by_name('mymodule.MyClass','path.to.module')`` is equivalent to
       ``from path.to.module.mymodule import MyClass as C``.
    """
    global __loaded_modules
    pieces = module_string.split('.')
    if len(pieces) == 1: # No dot
        filename = module_string.lower()
        class_name = module_string
    else:
        filename = pieces[-2]
        class_name = pieces[-1]
        if len(pieces) > 2: # Many dots
            if path is None:
                path = ".".join(pieces[:-2])
            else:
                path = ".".join([path] + pieces[:-2])
        
    try:
        # Cache already loaded modules
        old_modules = set(sys.modules)

        try:
            # Load module
            if path is not None:
                module = __import__(path, globals(), locals(), [filename]).__dict__[filename]
            else:
                module = __import__(filename)
        except Exception:
            raise
        finally:
            # Store the difference
            __loaded_modules = __loaded_modules.union(set(sys.modules) - old_modules)
        
        return module.__dict__[class_name]

    except ImportError:
        print("Module {} failed to load".format(filename))
        raise
    except KeyError:
        print("No class {} in module {}".format(class_name,filename))
        raise
