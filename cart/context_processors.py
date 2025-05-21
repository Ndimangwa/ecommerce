from .cart import Cart 

#Create Context Processor os that our cart may work on all pages

def CartProcessor(request):
    return {'cart' : Cart(request)}