import shutil
import tempfile

from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase

from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост больше 15 символов',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        post = PostModelTest.post
        self.assertEqual(
            str(group), group.title, "У групп неправильный __str__"
        )
        self.assertEqual(
            str(post), post.text[:15], "У постов неправильный __str__"
        )
