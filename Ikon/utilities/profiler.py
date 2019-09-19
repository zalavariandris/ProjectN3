def profile(f):
    import time
    def inner(*args, **kwargs):
        # storing time before function execution 
        begin = time.time() 
        print(f.__name__,"...")
        r = f(*args, **kwargs) 
  
        # storing time after function execution 
        end = time.time() 
        print("  ΔT:", end - begin)
        return r
    return inner