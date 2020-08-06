from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.auth.models import User
from .models import Post


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah",
                                             email="connor.s@skynet.com",
                                             password="12345")

    # После регистрации пользователя создается
    # его персональная страница (profile)
    def test_profile(self):
        # формируем GET-запрос к странице сайта
        response = self.client.get("/sarah/")

        # проверяем что страница найдена
        self.assertEqual(response.status_code, 200)

        # проверяем, что объект пользователя, переданный в шаблон,
        # соответствует пользователю, которого мы создали
        self.assertIsInstance(response.context["author"], User)
        self.assertEqual(response.context["author"].
                         username, self.user.username)

    # Авторизованный пользователь может опубликовать пост (new)
    def test_new_post_auth(self):
        login = self.client.login(username='sarah',
                                  password='12345')
        self.assertEqual(login, True)
        new_post = self.client.get("/new/")
        self.assertEqual(new_post.status_code, 200)

    # Неавторизованный посетитель не может опубликовать пост
    # (его редиректит на страницу входа)
    def test_new_post_not_auth(self):
        new_post_page = self.client.get("/new/")
        self.assertEqual(new_post_page.status_code, 302)
        self.assertRedirects(new_post_page,
                             "/auth/login/?next=/new/",
                             status_code=302,
                             target_status_code=200,
                             msg_prefix='')

    # После публикации поста новая запись появляется на главной
    # странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)
    def test_post_presence(self):
        login = self.client.login(username='sarah',
                                  password='12345')
        self.assertEqual(login, True)
        self.post = Post.objects.create(
                     text="It's driving me crazy!",
                     author=self.user)
        response_index = self.client.get("")
        self.assertEqual(response_index.status_code, 200)
        author_post = (response_index.context['paginator'].
                       object_list.first().author)
        self.assertEqual(author_post, self.user)

        # Проверям, есть ли новый пост на персональной странице автора

        response_profile = self.client.get("/sarah/")
        self.assertEqual(response_profile.status_code, 200)
        author_post_profile = (response_profile.context['paginator'].
                               object_list.first().author)
        self.assertEqual(author_post_profile, self.user)

        # Проверям, есть ли новый пост на странице поста
        post_id = Post.objects.get(author=self.user).id
        response_page = self.client.get(reverse('post',
                                                args=(self.user, post_id)))
        self.assertEqual(response_page.status_code, 200)
        author_post_page = response_page.context['post_author']
        self.assertEqual(author_post_page, self.user)

    # Авторизованный пользователь может отредактировать свой пост
    # и его содержимое изменится на всех связанных страницах
    def test_post_edit(self):

        login = self.client.login(username='sarah',
                                  password='12345')
        self.assertEqual(login, True)

        self.post = Post.objects.create(
            text="simple text",
            author=self.user)
        post_id = Post.objects.get(author=self.user).id

        self.client.post(reverse('post_edit', args=(self.user, post_id)),
                         data={'text': 'test text'}, follow=True)
        request = self.client.get(reverse('post_edit',
                                          args=(self.user, post_id)))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.context['post'].text, 'test text')

        request_response_profile = self.client.get("/sarah/")
        text_post_profile = (request_response_profile.context['paginator'].
                             object_list.first().text)
        self.assertEqual(text_post_profile, 'test text')

        request_response_page = self.client.get(reverse('post',
                                                args=(self.user, post_id)))
        text_post_profile = request_response_page.context['post'].text
        self.assertEqual(text_post_profile, 'test text')

        request_response_index = self.client.get("")
        text_post_profile = (request_response_index.context['paginator'].
                             object_list.first().text)
        self.assertEqual(text_post_profile, 'test text')
