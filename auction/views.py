from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
import datetime
from django.utils.timezone import now, localtime

from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from accounts.mixins import AictiveUserRequiredMixin, AictiveBidderRequiredMixin, AictiveSellerRequiredMixin, UserHasPaymentSystem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm

from accounts.models import Profile, PaymentCreditCard


from auction.models import Product, SubCategory, AuctionDate, AuctionSession, AuctionProduct, AuctionBidding, AuctionWinner, Category, SubCategory, SearchHistory
from auction.forms import ProductForm

from django.views import View, generic
# Create your views here.


def load_sub_categories(request):
    category_id = request.GET.get('category')
    sub_categories = SubCategory.objects.filter(
        category_id=category_id)
    return render(request, 'product/subcategories_dropdown_list_options.html', {'sub_categories': sub_categories})


def load_auction_session(request):
    auction_date_id = request.GET.get('auction_date')
    auction_session = AuctionSession.objects.filter(
        auction_date=auction_date_id)
    return render(request, 'product/auction_session_dropdown_list_options.html', {'auction_session': auction_session})


class HomeView(generic.ListView):
    model = AuctionProduct
    context_object_name = 'product_list'
    paginate_by = 10
    template_name = 'landing/home.html'

    def get_queryset(self):
        today = datetime.date.today()
        qs = AuctionProduct.objects.select_related('product').filter(
            product__auction_date__auction_date__gte=today)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context


class ProductListView(AictiveSellerRequiredMixin, UserHasPaymentSystem, generic.ListView):
    model = Product
    paginate_by = 20
    context_object_name = 'product_list'
    template_name = 'product/product_list.html'

    def get_queryset(self):
        qs = Product.objects.select_related(
            'category', 'sub_category', 'owner').filter(owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Product List'
        return context


class AddProductView(AictiveSellerRequiredMixin, UserHasPaymentSystem, SuccessMessageMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/add_product.html'
    success_message = 'Product Added SuccessFully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Product'
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class EditProductView(AictiveSellerRequiredMixin, UserHasPaymentSystem, SuccessMessageMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/edit_product.html'
    success_message = 'Product Update SuccessFully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Product'
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DeleteProductView(AictiveSellerRequiredMixin, UserHasPaymentSystem, SuccessMessageMixin, generic.edit.DeleteView):
    model = Product
    template_name = 'payment/delete_product.html'
    success_message = 'Product Deleted SuccessFully'
    success_url = reverse_lazy('auction:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Product'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteCreditCardView, self).delete(request, *args, **kwargs)


class TodayAuctionProductView(AictiveBidderRequiredMixin, UserHasPaymentSystem, generic.ListView):
    model = AuctionProduct
    context_object_name = 'product_list'
    paginate_by = 10
    template_name = 'auction/auction_product.html'

    def get_queryset(self):
        today = datetime.date.today()
        qs = AuctionProduct.objects.select_related('product').filter(
            product__auction_date__auction_date=today)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Today Auction Product'
        return context


class FutureAuctionProductView(AictiveBidderRequiredMixin, UserHasPaymentSystem, generic.ListView):
    model = AuctionProduct
    context_object_name = 'product_list'
    paginate_by = 10
    template_name = 'auction/auction_product.html'

    def get_queryset(self):
        today = datetime.date.today()
        qs = AuctionProduct.objects.select_related('product').filter(
            product__auction_date__auction_date__gt=today)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upcoming Auction Product'
        return context


class PreviousAuctionProductView(AictiveBidderRequiredMixin, UserHasPaymentSystem, generic.ListView):
    model = AuctionProduct
    context_object_name = 'product_list'
    paginate_by = 10
    template_name = 'auction/auction_product.html'

    def get_queryset(self):
        today = datetime.date.today()
        qs = AuctionProduct.objects.select_related('product').filter(
            product__auction_date__auction_date__lt=today)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Previous Auction Product'
        return context


class AuctionDetailsView(AictiveUserRequiredMixin, UserHasPaymentSystem, generic.DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'auction/auction_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title} -- Details'
        check = AuctionBidding.objects.select_related(
            'product', 'user').filter(product=self.object, user=self.request.user).first()
        context['bidding_check'] = check

        all_bidding = AuctionBidding.objects.select_related(
            'product', 'user').filter(product=self.object)

        context['all_bidding'] = all_bidding

        today = datetime.date.today()
        context['today'] = today
        context['time'] = localtime().time()
        return context


class ParticpateAuctionView(AictiveBidderRequiredMixin, UserHasPaymentSystem, View):
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product_obj = get_object_or_404(Product, id=product_id)

        today = datetime.date.today()
        if product_obj.auction_date.auction_date >= today:
            check = AuctionBidding.objects.select_related('product', 'user').filter(
                product=product_obj, user=request.user).first()
            if check:
                messages.info(request, 'Wait For Bidding Start Time')
                return redirect('auction:auction_details', product_id)
            else:
                AuctionBidding.objects.create(
                    product=product_obj, user=request.user)
                messages.info(
                    request, 'Thanks For Your Participation.Bidding Will Be Start On Time')
                return redirect('auction:auction_details', product_id)
        else:
            messages.info(
                request, 'This Auction Was Complted')
            return redirect('auction:auction_details', product_id)

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product_obj = get_object_or_404(Product, id=product_id)

        today = datetime.date.today()
        time = localtime().time()

        check = AuctionBidding.objects.select_related(
            'product', 'user').filter(product=product_obj, user=self.request.user).first()

        if check:
            if product_obj.auction_date.auction_date == today and product_obj.auction_session.auction_end_time >= time and product_obj.auction_session.auction_start_time <= time:

                amount = float(request.POST.get('amount'))
                if amount >= product_obj.min_price:
                    check.amount = amount
                    check.save()
                    return redirect('auction:auction_details', product_id)
                else:
                    messages.info(
                        request, 'Amount Must Be Greater Than Min Price Of The Product')
                    return redirect('auction:auction_details', product_id)
            elif product_obj.auction_date.auction_date > today:
                print('Future')
            else:
                print('Past')
        else:
            messages.info(
                request, 'Please First Click The Participate Button')
            return redirect('auction:auction_details', product_id)


class AuctionWinnerView(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product_obj = get_object_or_404(Product, id=product_id)

        winner = AuctionWinner.objects.filter(product=product_obj).first()

        context = {
            'product_obj': product_obj,
            'winner': winner,
            'titlte': 'Auction Result'
        }

        return render(request, 'auction/winner.html', context)


class SearchProductView(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category')
        sub_category_id = request.GET.get('sub_category')

        category_obj = get_object_or_404(Category, id=category_id)
        sub_category_obj = get_object_or_404(SubCategory, id=sub_category_id)

        check_history = SearchHistory.objects.filter(user=request.user).first()

        if check_history:
            check_history.category.add(category_obj)
            check_history.sub_category.add(sub_category_obj)
        else:
            serach_history = SearchHistory.objects.create(user=request.user)
            serach_history.category.add(category_obj)
            serach_history.sub_category.add(sub_category_obj)

        search_product = Product.objects.filter(
            category=category_obj, sub_category=sub_category_obj)
        context = {
            'product_list': search_product,
            'title': 'Search Result',
        }
        return render(request, 'auction/search_product.html', context)
