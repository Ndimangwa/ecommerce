from store.models import Product
class Cart():
    def __init__(self, request):
        self.session = request.session
        # Get the current session if exists
        cart = self.session.get('session_key')
        # if the user is new
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        #Make sure cart is available in all pages
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            pass
        else:
            product_qty = str(quantity)
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        #ourcart
        ourcart = self.cart
        #update product
        ourcart[product_id] = product_qty
        #Update session
        self.session.modified = True 
        #Not necessary to return
        return self.cart
    
    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
        else:
            pass

    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        #get ids from the cart
        product_ids = self.cart.keys()
        #use ids to look up products in db
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def get_total(self):
        #Get product ids
        product_ids = self.cart.keys()
        #Lookup products
        products = Product.objects.filter(id__in=product_ids)
        #quantities
        quantities = self.cart
        #start total
        total = 0
        #key, value
        for key, value in quantities.items():
            #to make search in object, value is quantity 
            # {'4':5, '1':7}
            key = int(key)
            for product in products:
                if product.id == key:
                    price = product.sale_price if product.is_sale else product.price
                    total += price * value
        return total