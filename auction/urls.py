from django.urls import path
from . import views

app_name = "auction"
urlpatterns = [
    path('add-product/', views.AddProductView.as_view(), name="add_product"),
    path('ajax/load-sub-categories/', views.load_sub_categories,
         name='ajax_load_sub_categories'),
    path('ajax/load-auction-session/', views.load_auction_session,
         name='ajax_load_auction_session'),
    path('product_list/', views.ProductListView.as_view(), name="product_list"),
    path('edit-product/<int:pk>',
         views.EditProductView.as_view(), name="edit_product"),
    path('delete-product/<int:pk>',
         views.DeleteProductView.as_view(), name="delete_product"),


    path('today/auction-produc/', views.TodayAuctionProductView.as_view(),
         name='today_auction_product'),
    path('future/auction-produc/', views.FutureAuctionProductView.as_view(),
         name='future_auction_product'),
    path('previous/auction-produc/', views.PreviousAuctionProductView.as_view(),
         name='previous_auction_product'),

    path('details/<int:pk>/', views.AuctionDetailsView.as_view(),
         name='auction_details'),

    path('particpate/<int:product_id>/', views.ParticpateAuctionView.as_view(),
         name='participate_auction'),


    path('winner/<int:product_id>/', views.AuctionWinnerView.as_view(),
         name='auction_winner'),


    path('search/product/', views.SearchProductView.as_view(),
         name='search_product'),
]
