import importlib
import os


def get_funcs(func_name):
    this_path = os.path.dirname(__file__)
    module_list = [f for f in os.listdir(this_path) if (f.endswith(".py")) and (f != "__init__.py")]
    path_list = ["." + os.path.splitext(f)[0] for f in module_list]

    functions = []
    for path in path_list:
        module = importlib.import_module(path, package=__package__)
        if hasattr(module, func_name):
            functions += [getattr(module, func_name)]
        
    return functions


def register_package():
    for func in get_funcs("register"):
        func()


def unregister_package():
    for func in get_funcs("unregister"):
        func()
