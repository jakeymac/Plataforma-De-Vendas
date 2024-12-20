from django.shortcuts import render, redirect
from .models import Product, ProductSubcategory, InitialProductState, InitialProductImage


def add_product_view(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        return render(request, 'products/add_new_product.html')
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect('home')
    
def edit_product_view(request, product_id):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        product = Product.objects.get(id=product_id)

        initial_product_state = InitialProductState.objects.create(
            product=product,
            store=product.store,
            sub_category=product.sub_category,
            product_name=product.product_name,
            description=product.description,
            properties=product.properties,
            is_active=product.is_active,
            draft=product.draft,
        )

        images = product.productimage_set.all().order_by('order')
        for image in images:
            InitialProductImage.objects.create(
                product = initial_product_state,
                image = image.image,
                order=image.order,
                s3_key=image.s3_key,
                created_at=image.created_at,
                updated_at=image.updated_at,
            )
        
        properties = product.properties
        subcategories = ProductSubcategory.objects.all()
        return render(request, 'products/edit_product.html', {'product': product, 'initial_product_state': initial_product_state, 
                                                              'images': images, 'subcategories': subcategories, 'properties': properties})
    
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect('home')
