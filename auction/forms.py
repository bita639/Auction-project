from django import forms
from django.forms import FileInput
from django.forms import ModelForm
from auction.models import Product, SubCategory, AuctionSession, AuctionDate


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ('owner', 'active', 'rejected',
                   'created_at', 'added_to_auction')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategory.objects.none()
        self.fields['auction_session'].queryset = AuctionSession.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(
                    category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.subcategories

        if 'auction_date' in self.data:
            try:
                auction_date_id = int(self.data.get('auction_date'))
                self.fields['auction_session'].queryset = AuctionSession.objects.filter(
                    auction_date_id=auction_date_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['auction_session'].queryset = self.instance.auction_date.auction_date_session
