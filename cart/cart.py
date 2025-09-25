from store.models import Product, Profile
#from django.contrib import messages
class Cart():
    def __init__(self, request):
        self.session = request.session
        #get request to the object
        self.request = request
        # Get the current session if exists
        cart = self.session.get('session_key')
        # if the user is new
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        #Make sure cart is available in all pages
        self.cart = cart

    def persist_cart(self):
        if self.request.user.is_authenticated:
            #get current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #convert the cart from dictionary (single-quote) to JSON (double-quote)
            #JSON does not support single-quote
            # from {'3':1, '7': 4} to {"3": 1, "7": 4}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #let save our cart
            current_user.update(old_cart=carty)

    def merge_carts(self, old_cart):
        #old_cart dictionary
        #resultant_cart = old_cart + session_items
        session_cart = self.cart 
        # We have two dictionaries we need to merge
        # if item exists in both, we need to 
        # Add their quantities
        new_cart = {};
        if old_cart:
            new_cart = old_cart.copy()
        if session_cart:
            for key, quantity in session_cart.items():
                #new_cart[key] = new_cart[key] + quantity if new_cart[key] else quantity
                qty = 0
                if key in new_cart:
                    qty = new_cart[key] + quantity
                else:
                    qty = quantity
                new_cart[key] = qty
        print("**********************")
        print(new_cart)
        print("**********************")
        #Now we have a new_cart dictionary
        #Add everything in bulk not one by one
        #self.cart = new_cart 
        #Let update cart manually
        for key, value in new_cart.items():
            self.cart[key] = value
        self.session.modified = True
        #Now persist data
        self.persist_cart()
    
    def add(self, product, quantity):
        product_id = str(product.id)
        self.add_id(product_id, quantity)

    def add_id(self, product_id, quantity):
        if product_id in self.cart:
            pass
        else:
            product_qty = str(quantity)
            self.cart[product_id] = int(product_qty)

        self.session.modified = True
        #Saving the cart, only for logged-in user
        self.persist_cart()
        
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        #ourcart
        ourcart = self.cart
        #update product
        ourcart[product_id] = product_qty
        #Update session
        self.session.modified = True 
        #Saving the cart, only for logged-in user
        self.persist_cart()
        #Not necessary to return
        return self.cart
    
    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            #Saving the cart, only for logged-in user
            self.persist_cart()
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