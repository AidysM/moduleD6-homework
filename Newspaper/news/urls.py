from django.urls import path
from .views import PostList, PostDetailView, Search, PostCreateView
from .views import PostDeleteView, PostUpdateView, subscribe_me
                # импортируем наши представления

urlpatterns = [
    # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым,
    # позже станет ясно почему
    path('', PostList.as_view()),
    # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого
    # вызываем метод as_view
    path('<int:pk>', PostDetailView.as_view(), name='post'),
    # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('search/', Search.as_view()),
    path('create/', PostCreateView.as_view(), name='post_create'), # Ссылка на создание товара
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<int:pk>/subscribe/', subscribe_me, name='subscribe'),
]
