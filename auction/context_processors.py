from .models import Category, SubCategory


def category_list(request):
    category_list = Category.objects.all()
    return {'category_list': category_list}


def subcategory_list(request):
    subcategory_list = SubCategory.objects.all()
    return {'subcategory_list': subcategory_list}
