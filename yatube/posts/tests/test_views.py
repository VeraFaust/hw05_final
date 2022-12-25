import shutil
import tempfile

from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django import forms

from posts.models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тест-заголовок группы',
            slug='test-slug',
            description='Тест-описание группы',
        )
        cls.group_2 = Group.objects.create(
            title='group_post_2',
            slug='test-slug_2',
            description='Тест-описание группы_2'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тест-описание поста',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.post_2 = Post.objects.create(
            text='Тест-описание поста',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.other_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def create_follower(self):
        auth_client = User.objects.create_user(username='follow')
        self.authorized_client.force_login(auth_client)

    def pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
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
        for name, template in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_group_post_2_page_show_correct_context(self):
        """Пост group_post_2 не попал в группу,
        для которой не предназначен"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertIn('page_obj', response.context)
        first_object = self.assertNotEqual(
            len(
                response.context['page_obj']
            ),
            0
        )
        first_object = response.context['page_obj'][0]
        self.assertNotEqual(first_object.group, self.group_2)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован
        с правильным контекстом"""
        post_img = Post.objects.create(
                text='Тест-описание поста',
                author=self.user,
                group=self.group,
                image=self.post.image
            )
        response = self.authorized_client.get(
            reverse(
                'posts:index'
            )
        )
        page_obj = response.context['page_obj']
        for post in Post.objects.select_related('author', 'group'):
            self.assertIn('page_obj', response.context)
            self.assertIn(post, page_obj)
            self.assertEqual(post_img.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом"""
        post_img = Post.objects.create(
                text='Тест-описание поста',
                author=self.user,
                group=self.group,
                image=self.post.image
            )
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            )
            self.assertIn('page_obj', response.context)
            page_obj = response.context['page_obj']
            self.assertEqual(
                response.context['group'],
                self.group
            )
            self.assertIn(post, page_obj)
            self.assertIn('page_obj', response.context)
            self.assertEqual(post_img.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован
        с правильным контекстом"""
        post_img = Post.objects.create(
                text='Тест-описание поста',
                author=self.user,
                group=self.group,
                image=self.post.image
            )
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            )
            self.assertIn('page_obj', response.context)
            page_obj = response.context['page_obj']
            self.assertEqual(
                response.context['author'],
                self.user
            )
            self.assertIn(post, page_obj)
            self.assertIn('page_obj', response.context)
            self.assertEqual(post_img.image, self.post.image)

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.assertIn('post', response.context)
        post_context = response.context['post']
        self.assertEqual(post_context, self.post)
        self.assertEqual(post_context.image, self.post.image)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post.html сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_create'
            )
        )
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, excepted in fields.items():
            with self.subTest(value=value):
                self.assertIn('form', response.context)
                fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(fields, excepted)
            self.assertIn('user', response.context)
            name_context = response.context['user']
            self.assertEqual(name_context, self.user)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit.html сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, excepted in fields.items():
            with self.subTest(value=value):
                self.assertIn('form', response.context)
                fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(fields, excepted)
            self.assertIn('user', response.context)
            name_context = response.context['user']
            self.assertEqual(name_context, self.user)
            self.assertIn('is_edit', response.context)
            is_edit_context = response.context.get('is_edit')
            self.assertTrue(is_edit_context)

    def test_post_page_(self):
        """Пост с группой находятся в нужных страницах"""
        field_urls_templates = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug
                }
            ),
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.username
                }
            )
        ]
        for url in field_urls_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('page_obj', response.context)
                self.assertEqual(len(response.context['page_obj']), 2)

    def test_cache_index_page(self):
        """Проверка работы кеша главной страницы"""
        cache.clear()
        url = reverse('posts:index')
        response = self.authorized_client.get(url)
        cache_check = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response = self.authorized_client.get(url)
        self.assertEqual(response.content, cache_check)
        cache.clear()
        response = self.authorized_client.get(url)
        self.assertNotEqual(response.content, cache_check)

    def test_authorized_client_follow(self):
        """Подписка авторизованным клиентом
        на других пользователей"""
        follow_count = Follow.objects.count()
        self.create_follower()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_authorized_client_unfollow(self):
        """Отписка авторизованным клиентом
        от других пользователей"""
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        ).delete()
        follow_count = Follow.objects.count()
        self.create_follower()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username}
            ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        cache.clear()

    def test_new_post_for_followers(self):
        """Отображение постов в ленте у подписчиков"""
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_post, first_object)

    def test_new_post_for_unfollow(self):
        """Отсутсвтие постов в ленте у гостя"""
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    posts_on_first_page = 10
    posts_on_second_page = 3
    NUM_PAGE = posts_on_first_page + posts_on_second_page

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        for i in range(PaginatorViewsTest.NUM_PAGE):
            Post.objects.create(
                text=f'Пост #{i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах"""
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_).context.get('page_obj')),
                    PaginatorViewsTest.posts_on_first_page
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    PaginatorViewsTest.posts_on_second_page
                )
