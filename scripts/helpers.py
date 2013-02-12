class Struct:
    def __str__(self):
        return "\{{}\}".format(", ".join(["{} : {}".format(k,v) for k,v in self.__dict__.items()]))
        #return str(self.__dict__)

def load_by_name(module_string, path = None):
    try:
        filename, class_name = module_string.split(".")
    except ValueError:
        # either too many or too few dots
        # fallback to capitalization
        filename = module_string.lower()
        class_name = module_string.capitalize()
        
    try:
        if path is not None:
            module = __import__(path, globals(), locals(), [filename]).__dict__[filename]
        else:
            module = __import__(filename)
        controller_class = module.__dict__[class_name]
        return (module, controller_class)
    except ImportError:
        print "Module {} failed to load".format(filename)
        raise
    except KeyError:
        print "No class {} in module {}".format(class_name,filename)
        raise
