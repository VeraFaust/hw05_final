import shutil
import tempfile

from http import HTTPStatus
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_auth = User.objects.create(username='auth_2')
        cls.group = Group.objects.create(
            title='Тест-название группы',
            slug='test-slug',
            description='Тест-описание',
        )
        cls.new_group = Group.objects.create(
            title='Новая тест-группа',
            slug='new-slug',
            description='Тест-описание новой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест-текст',
            group=cls.group
        )
        cls.form = PostForm(instance=cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.other_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.auth_client = Client()
        self.auth_client.force_login(self.user_auth)

    def test_create_post_other_client(self):
        """Создание поста неавторизованным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый текст',
        }
        response = self.other_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_edit_post_authorized_client(self):
        """Редактирование поста авторизованным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.new_group.pk,
            'text': 'test',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post_change = Post.objects.get(id=self.post.pk)
        self.assertEqual(
            form_data['group'],
            post_change.group.pk
        )
        self.assertEqual(
            form_data['text'],
            post_change.text
        )
        self.assertEqual(post_change.author, self.user)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )

    def test_edit_post_other_client(self):
        """Редактирование поста неавторизованным пользователем"""
        AUTH_LOGIN = reverse('users:login')
        EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        posts_count = Post.objects.count()
        form_data = {
            'group': self.new_group,
            'text': 'test',
        }
        response = self.other_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(
            response,
            f'{AUTH_LOGIN}?next={EDIT}'
        )

    def test_edit_post_auth_client(self):
        """Редактирование поста не автором поста"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.new_group,
            'text': 'test',
        }
        response = self.auth_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )

    def test_authorized_client_comment(self):
        """Комментирование поста авторизованным пользователем"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тест-коментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.get(id=self.post.pk)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post_id, self.post.pk)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )

    def test_other_client_comment(self):
        """Комментирование поста неавторизованным пользователем"""
        AUTH_LOGIN = reverse('users:login')
        COMMENT = reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}
        )
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.other_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            f'{AUTH_LOGIN}?next={COMMENT}'
        )
