from celery.decorators import task
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.core.mail import EmailMessage


@task()
def set_bidding_winner(product_id):
    from .models import Product, AuctionWinner, AuctionBidding
    product_object = get_object_or_404(Product, id=product_id)

    max_amount = AuctionBidding.objects.filter(
        product=product_object
    ).aggregate(max_amount=Max('amount'))['max_amount']
    winner = AuctionBidding.objects.filter(
        product=product_object, amount=max_amount).first()

    print(winner)

    if winner:
        AuctionWinner.objects.create(
            product=product_object, user=winner.user, amount=winner.amount, is_complted=True)
    else:
        AuctionWinner.objects.create(product=product_object)


@shared_task
def send_email_for_similar_product(product_id):
    from .models import Product, SearchHistory
    product_obj = get_object_or_404(Product, id=product_id)

    category = product_obj.category
    sub_category = product_obj.sub_category

    search_history = SearchHistory.objects.filter(
        category__id=category.id, sub_category__id=sub_category.id)

    for history in search_history:
        subject = f'New Product Suggestion Based On Your Search History'
        message = f'New Product Added On {category} -- {sub_category}'
        email = EmailMessage(subject, message, to=[history.user.email])
        email.send()
