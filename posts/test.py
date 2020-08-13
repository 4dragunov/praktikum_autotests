from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.auth.models import User
from .models import Post, Group


class ProfileTest(TestCase):

    def check_post_in_page(self, url, text, user, group):
        response = self.client_auth.get(url)
        paginator = response.context.get('paginator')
        if paginator is not None:
            self.assertEqual(paginator.count, 1)
            post = response.context['page'][0]
        else:
            post = response.context['post']
        self.assertEqual(post.text, text)
        self.assertEqual(post.author, user)
        self.assertEqual(post.group, group)

    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(username="sarah")
        self.client_auth.force_login(self.user)

        self.client_unauth = Client()

    # После регистрации пользователя создается
    # его персональная страница (profile)
    def test_creation_profile_page_after_reg(self):
        response = self.client_auth.get(reverse('profile', args=(self.user,)))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["author"], User)
        self.assertEqual(response.context["author"].
                         username, self.user.username)

    # Авторизованный пользователь может опубликовать пост (new)
    def test_auth_user_can_publish_post(self):
        new_post = self.client_auth.get(reverse('new_post'))
        self.assertEqual(new_post.status_code, 200)

    # Неавторизованный посетитель не может опубликовать пост
    # (его редиректит на страницу входа)
    def test_unauth_user_cant_publish_post(self):
        new_post_page = self.client_unauth.get(reverse('new_post'))
        self.assertEqual(new_post_page.status_code, 302)
        self.assertRedirects(new_post_page,
                             "/auth/login/?next=/new/",
                             status_code=302,
                             target_status_code=200,
                             msg_prefix='')

    # После публикации поста новая запись появляется на главной
    # странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)

    def test_post_appears_on_pages(self):

        self.group = Group.objects.create(title="test")

        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )

        urls = (reverse('index'),
                reverse('profile', args=(self.user.username,)),
                reverse('post', args=(self.user.username, self.post.id,)),
                )

        for url in urls:
            self.check_post_in_page(url, 'Test text', self.user, self.group)

    # Авторизованный пользователь может отредактировать свой пост
    # и его содержимое изменится на всех связанных страницах

    def test_auth_user_can_edit_post_appears_on_pages(self):

        self.group = Group.objects.create(title="test", slug="test")

        self.post = Post.objects.create(
            text="simple text",
            author=self.user,
            group=self.group
        )

        self.client_auth.post(reverse('post_edit',
                                      args=(self.user, self.post.id,)),
                              data={'text': 'Test text',
                                    'author': self.user.username,
                                    'group': self.group.id})

        urls = (reverse('index'),
                reverse('profile', args=(self.user.username,)),
                reverse('post', args=(self.user.username, self.post.id,)),
                reverse('group_url', args=(self.group.slug,)),
                )

        for url in urls:
            self.check_post_in_page(url, 'Test text', self.user, self.group)
