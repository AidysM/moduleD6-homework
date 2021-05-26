from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, reverse, redirect
from django.core.mail import mail_admins, send_mail # импортируем функцию для массовой отправки писем админам
from datetime import datetime
from django.views import View
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string # импортируем функцию, которая срендерит наш html в текст
from django.contrib.auth.decorators import login_required
    # импортируем класс, который говорит нам о том, что
    # в этом представлении мы будем выводить список объектов из БД
from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm


class PostList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'posts.html'  # указываем имя шаблона, в котором будет лежать html, в
        # котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты,
        # его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    queryset = Post.objects.order_by('-post_date')
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
    template_name = 'post.html' # название шаблона будет post.html
    #context_object_name = 'post' # название объекта. в нём будет
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscribe'] = not Category.objects.filter(subscribers=self.request.user.pk)
        return context


class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-post_date']
    paginate_by = 10 # поставим постраничный вывод в 10 элементов

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя
            # метод get_context_data у наследуемого класса (привет полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())  # вписываем наш
                                                                # фильтр в контекст
        return context


def mail_subscr(name, text, categ):
    cats = Category.objects.filter(category=categ)
    for cat in cats:
        subscs = Category.subscribers.all()
        for subsc in subscs:
            send_mail(
                subject=name,
                # имя клиента и дата записи будут в теме для удобства
                message=text,  # сообщение с кратким описанием проблемы
                from_email='mongushit@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
                recipient_list=[subsc.user.email, ]
                # здесь список получателей. Например, секретарь, сам врач и т. д.
            )



class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    template_name = 'post_create.html'
    form_class = PostForm
    success_url = '/news/'

    mail_subscr(form_class.Meta.model.post_name,
                form_class.Meta.model.content,
                form_class.Meta.model.category)


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


class PostView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'post_create.html', {})

    def post(self, request, *args, **kwargs):
        post = Post(
            post_date=datetime.strptime(request.POST['post_date'], '%Y-%m-%d'),
            post_name=request.POST['post_name'],
            content=request.POST['content'],
        )
        post.save()

        # отправляем письмо
        send_mail(
            subject=f'{post.post_name} {post.post_date.strftime("%Y-%M-%d")}',
            # имя клиента и дата записи будут в теме для удобства
            message=post.content,  # сообщение с кратким описанием проблемы
            from_email='mongushit@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
            recipient_list=['mongushit79@gmail.com', ]
            # здесь список получателей. Например, секретарь, сам врач и т. д.
        )

        # получем наш html
        html_content = render_to_string(
            'post.html',
            {
                'post': post,
            }
        )
        # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'{post.post_name} {post.post_date.strftime("%Y-%M-%d")}',
            body=post.content,  # это то же, что и message
            from_email='mongushit@yandex.ru',
            to=['mongushit79@gmail.com'],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        msg.send()  # отсылаем

        # отправляем письмо всем админам по аналогии с send_mail, только здесь получателя указывать не надо
        mail_admins(
            subject=f'{post.post_name} {post.post_date.strftime("%d %m %Y")}',
            message=post.content,
        )

        return redirect('news:post')


@login_required
def subscribe_me(request):
    # user = request.user
    # path = request.path
    pathlist = request.path.split('/')
    post_id = int(pathlist[-3])
    if not Category.objects.filter(subscribers=request.user.pk):
        post = Post.objects.get(id=post_id)
        cat = Category.objects.get(category=post.category)
        cat.subscribers.create(pk=user.pk)
    return redirect('news/')

