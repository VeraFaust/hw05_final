import shutil
import tempfile

from http import HTTPStatus

from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_auth = User.objects.create(username='auth_2')
        cls.group = Group.objects.create(
            title='Тест-название группы',
            slug='test-slug',
            description='Тест-описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
        )

    def setUp(self):
        self.other_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.auth_client = Client()
        self.auth_client.force_login(self.user_auth)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_url_reverse_create_post(self):
        url_reverse = {
            reverse('posts:index'): '/',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): f'/group/{self.group.slug}/',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): f'/profile/{self.user.username}/',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): f'/posts/{self.post.pk}/',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): f'/posts/{self.post.pk}/edit/',
            reverse('posts:post_create'): '/create/',
        }
        for name, url in url_reverse.items():
            with self.subTest(
                name=name,
                url=url
            ):
                self.assertEqual(name, url)

    def test_url_exists_at_desired_location(self):
        """Доступ к страницам для любых пользователей."""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ),
        ]
        for request_client in (
            self.other_client,
            self.authorized_client,
            self.auth_client
        ):
            for url in urls:
                with self.subTest(
                    url=url,
                    request_client=request_client
                ):
                    response = request_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location(self):
        """Доступ авторизованному пользователю
        на создание и редактирование поста."""
        urls = [
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            reverse('posts:post_create'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_other_client(self):
        """Редирект со страницы create_post для
        неавторизованного пользователя."""
        AUTH_LOGIN = reverse('login')
        NEW = reverse('posts:post_create')
        response = self.other_client.get(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertRedirects(
            response,
            f'{AUTH_LOGIN}?next={NEW}'
        )

    def test_post_edit_url_redirect_other_client(self):
        """Редирект со страницы post_edit для
        неавторизованного пользователя."""
        AUTH_LOGIN = reverse('users:login')
        EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        response = self.other_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            f'{AUTH_LOGIN}?next={EDIT}'
        )

    def test_post_edit_url_redirect_auth_client(self):
        """Редирект со страницы post_edit
        для не автора поста."""
        EDIT_AUTH = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        response = self.auth_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            EDIT_AUTH
        )

    def test_unexisting_page_users(self):
        """Возврат ошибки 404 пользователям
        при запросе к unexisting_page
        и проверка его шаблона."""
        url_page_error_2 = '/unexisting_page/'
        for url_clients in (
            self.other_client,
            self.authorized_client,
            self.auth_client
        ):
            response = url_clients.get(url_page_error_2)
            self.assertEqual(
                response.status_code,
                HTTPStatus.NOT_FOUND
            )
            self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
