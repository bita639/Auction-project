from django.contrib import admin
from auction.models import AuctionDate, AuctionSession, Category, SubCategory, Product, AuctionProduct, AuctionBidding, AuctionWinner, SearchHistory
# Register your models here.


class AuctionSessionline(admin.StackedInline):
    model = AuctionSession
    extra = 1
    exclude = ['auction_end_time', 'end_time']


class AuctionDateAdmin(admin.ModelAdmin):
    inlines = [
        AuctionSessionline
    ]
    list_display = ['auction_date']
    search_fields = ('auction_date',)


admin.site.register(AuctionDate, AuctionDateAdmin)


class SubCategoryline(admin.StackedInline):
    model = SubCategory
    extra = 1


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('sub_category_name',)
    search_fields = ('sub_category_name',)
    list_filter = ('sub_category_name',)
    list_per_page = 20


admin.site.register(SubCategory, SubCategoryAdmin)


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        SubCategoryline
    ]
    list_display = ['category_name']
    list_filter = ['category_name']
    search_fields = ('category_name',)


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'category',
                    'sub_category', 'active', 'rejected', 'added_to_auction', 'created')
    search_fields = ('owner__username', 'title', 'category', 'sub_category',)
    list_filter = ('owner__username', 'active',
                   'rejected', 'category', 'sub_category',)
    list_per_page = 20
    list_editable = ['active', 'rejected', 'added_to_auction']
    autocomplete_fields = ['owner', 'category']


# Register your models here.
admin.site.register(Product, ProductAdmin)


class AuctionProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_owner', 'product_category',
                    'product_sub_category', 'auction_date', 'auction_session')
    search_fields = ('product__title', 'product__owner__username',
                     'product__category__category_name', 'product__sub_category__sub_category_name',)
    list_per_page = 20

    def product_owner(self, obj):
        return obj.product.owner.username.title()

    def product_category(self, obj):
        return obj.product.category.category_name

    def product_sub_category(self, obj):
        return obj.product.sub_category.sub_category_name

    def auction_date(self, obj):
        return obj.product.auction_date.auction_date

    def auction_session(self, obj):
        return obj.product.auction_session


# Register your models here.
admin.site.register(AuctionProduct, AuctionProductAdmin)


class AuctionWinnerAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'amount', 'is_complted')
    search_fields = ('user__username', 'product__title', 'amount')
    list_filter = ('is_complted',)
    list_per_page = 20


# Register your models here.
admin.site.register(AuctionWinner, AuctionWinnerAdmin)


class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'category__category_name',
                     'sub_category__sub_category_name')
    list_per_page = 20


# Register your models here.
admin.site.register(SearchHistory, SearchHistoryAdmin)
