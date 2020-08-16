from django.db import models
from taggit.managers import TaggableManager
from taggit.models import Tag
from smart_selects.db_fields import GroupedForeignKey
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import set_bidding_winner, send_email_for_similar_product
import datetime
# Create your models here.


class AuctionDate(models.Model):
    auction_date = models.DateField()

    class Meta:
        verbose_name = 'AuctionDate'
        verbose_name_plural = '1. AuctionDate'

    def __str__(self):
        return str(self.auction_date)


class AuctionSession(models.Model):
    auction_date = models.ForeignKey(
        AuctionDate, on_delete=models.CASCADE, related_name='auction_date_session')
    auction_start_time = models.TimeField()
    auction_end_time = models.TimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):

        self.auction_end_time = self.auction_start_time.replace(
            hour=(self.auction_start_time.hour + 1) % 24)
        self.end_time = datetime.datetime.combine(
            self.auction_date.auction_date, self.auction_end_time)

        super(AuctionSession, self).save(*args, **kwargs)

    def __str__(self):
        return f"Start Time {self.auction_start_time} -- End Time {self.auction_end_time}"


class Category(models.Model):
    category_name = models.CharField(max_length=150, unique=True)

    class Meta():
        ordering = ['-id']
        verbose_name_plural = "2.Categories"

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, related_name='subcategories', on_delete=models.CASCADE, blank=True, null=True,)
    sub_category_name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.sub_category_name

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "3.SubCategory"


class Product(models.Model):
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='user_product')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category_product')
    sub_category = GroupedForeignKey(
        SubCategory, "category", on_delete=models.CASCADE, related_name='subcategory_product')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="product")
    min_price = models.FloatField()
    active = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    created = models.DateField(default=datetime.date.today)
    auction_date = models.ForeignKey(
        AuctionDate, on_delete=models.CASCADE, related_name='auction_date_product')
    auction_session = models.ForeignKey(
        AuctionSession, on_delete=models.CASCADE, related_name='auction_session_product')

    added_to_auction = models.BooleanField(default=False)
    tags = TaggableManager()

    def get_absolute_url(self):
        return reverse('auction:product_list')

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "4.Products"

    def __str__(self):
        return self.title


class AuctionProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='auction_products')

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "5.Auction Products"

    def save(self, *args, **kwargs):
        create_task = False
        if self.pk is None:
            create_task = True
        super(AuctionProduct, self).save(*args, **kwargs)

        if create_task:
            set_bidding_winner.apply_async(
                args=[self.product.id], eta=self.product.auction_session.end_time)

    def __str__(self):
        return self.product.title


class AuctionBidding(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='user_bidding')
    amount = models.FloatField(default=0.0, null=True, blank=True)

    class Meta():
        verbose_name_plural = "6.AuctionBidding"

    def __str__(self):
        return self.product.title


class AuctionWinner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='winner', null=True, blank=True)
    amount = models.FloatField(default=0.0, null=True, blank=True)
    is_complted = models.BooleanField(default=False)

    class Meta():
        verbose_name_plural = "7.AuctionWinner"

    def __str__(self):
        return 'winner'


class SearchHistory(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    sub_category = models.ManyToManyField(SubCategory)

    class Meta():
        verbose_name_plural = "8.SearchHistory"

    def __str__(self):
        return 'Search History'


@receiver(post_save, sender=Product)
def add_product_to_auction(sender, instance, created, **kwargs):
    if instance.active and not instance.added_to_auction:
        send_email_for_similar_product.delay(instance.id)

        AuctionProduct.objects.create(product=instance)
        instance.added_to_auction = True
        instance.save()
