def profile(func):
    import time
    def inner(*args, **kwargs):
        # storing time before function execution 
        begin = time.time() 
        print("---",func.__name__,"---")
        func(*args, **kwargs) 
  
        # storing time after function execution 
        end = time.time() 
        print("---Total time taken in : ", func.__name__, end - begin)
    return inner