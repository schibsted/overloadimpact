import liclient

def show_methods():
    obj = liclient.client
    methods = [x for x in dir(obj) if x[0:1] != '_' if callable(getattr(obj, x))]
    print 'Load Impact client methods:'
    print '\n'.join(methods)

def run_method(name, args):
    obj = liclient.client
    method = getattr(obj, name)
    output = method(*args)
    print(output)
