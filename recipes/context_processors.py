from .models import Cart, Tag

def counter(request):
    if request.user.is_authenticated:
        return {"counter": Cart.objects.filter(user=request.user).all().count()}
    return {'counter': []}

def check_cart(request):
    cart_list = []
    if request.user.is_authenticated:

        cart = Cart.objects.filter(user=request.user).all()

        for item in cart:
            cart_list.append(item.recipe.title)
    return {'cart_list': cart_list}  
 
    

def get_tags(request):
    return {'tags': Tag.objects.all()}

def url_filters(request):
    result = ''
    for item in request.GET.getlist('filters'):
        result += f'&filters={item}'
    return {'filters': result}
    
