from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = {
            'text',
            'group',
            'image',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа нового поста',
            'image': 'Новое изображение',
        }
        labels = {
            'text': 'Текст поста',
            'image': 'Картинка',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {
            'text': 'Напишите комментарий',
        }
        labes = {
            'text': 'Текст комментария',
        }
