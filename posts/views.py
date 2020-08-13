from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect, Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, Group

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  "group.html",
                  {"group": group, 'page': page, 'paginator': paginator, })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("index")

    form = PostForm()
    return render(request, "new_post.html", context={"form": form})


def profile(request, username):
    is_user_author = False
    if not User.objects.filter(username=username).exists():
        raise Http404("К сожалению запрашиваемый пользователь/"
                      " еще не зарегистрирован")
    author = User.objects.get(username=username)

    if str(author) == str(request.user):
        is_user_author = True

    profile_posts = Post.objects.filter(author=author)

    total_posts = Post.objects.filter(author__username=username).count()

    paginator = Paginator(profile_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html',
                  context={'page': page,
                           'paginator': paginator,
                           'total_posts': total_posts,
                           'author': author,
                           'profile_posts': profile_posts,
                           'is_user_author': is_user_author,})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_user_author = False
    post_author = User.objects.get(username=username)
    post_count = Post.objects.filter(author__username=post_author).count()
    print(post_count)

    if request.user == post_author:
        is_user_author = True

    return render(request, 'post.html', {'post_author': post_author,
                                         'post': post,
                                         'is_user_author': is_user_author,
                                         'post_count': post_count
                                         })

@login_required
def post_edit(request, username, post_id):
    is_form_edit = True
    post = get_object_or_404(Post, author__username=username, pk__iexact=post_id)
    if post.author == request.user:
        bound_form = PostForm(request.POST or None, instance=post)
        if bound_form.is_valid():
            post = bound_form.save()
            return redirect('post', username, post_id)

        form = PostForm(instance=post)

        return render(request, "new_post.html",
                      context={'form': form,
                               "is_form_edit": is_form_edit,
                               'post': post})
    else:
        return redirect('index')
