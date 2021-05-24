from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
    # импортируем класс, который говорит нам о том, что
    # в этом представлении мы будем выводить список объектов из БД
from .models import Post
from .filters import PostFilter
from .forms import PostForm


class PostList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'posts.html'  # указываем имя шаблона, в котором будет лежать html, в
        # котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты,
        # его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    queryset = Post.objects.order_by('-created')
    paginate_by = 10

    # метод get_context_data нужен нам для того, чтобы мы могли передать переменные в шаблон.
    # В возвращаемом словаре context будут храниться все переменные. Ключи этого словари и есть
    # переменные, к которым мы сможем потом обратиться через шаблон
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())  # вписываем фильтр
        return context



# создаём представление в котором будет детали конкретного отдельного товара
class PostDetailView(DetailView):
    #model = Post # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'post.html' # название шаблона будет product.html
    #context_object_name = 'post' # название объекта. в нём будет
    queryset = Post.objects.all()


class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-created']
    paginate_by = 10 # поставим постраничный вывод в 10 элементов

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя
            # метод get_context_data у наследуемого класса (привет полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())  # вписываем наш
                                                                # фильтр в контекст
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    template_name = 'post_create.html'
    form_class = PostForm
    success_url = '/news/'


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    template_name = 'post_create.html'
    form_class = PostForm
    success_url = '/news/'
    # метод get_object мы используем вместо queryset, чтобы получить информацию
    # об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'




