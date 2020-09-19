from .models import Cart, Tag

def counter(request):
    if request.user.is_authenticated:
        return {"counter": Cart.objects.filter(user=request.user).count()}
    return {'counter': []}

def check_cart(request):
    cart_list = []
    if request.user.is_authenticated:

        cart = Cart.objects.filter(user=request.user).all()
        cart_list = cart.values_list('recipe', flat=True)

    return {'cart_list': cart_list}  
 
    

def get_tags(request):
    return {'tags': Tag.objects.all()}

def url_filters(request):
    filters = request.GET.getlist('filters')
    filters.insert(0, '')
    filters = '&filters='.join(filters)
    return {'filters': filters}
    
