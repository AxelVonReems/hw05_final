from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Follow, Group, Post

User = get_user_model()

POSTS_ON_1ST_PAGE = 10
POSTS_ON_2ND_PAGE = 3


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.public_templates = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}),
                'posts/group_list.html'),
            (reverse(
                'posts:profile', kwargs={'username': cls.user}),
                'posts/profile.html'),
            (reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}),
                'posts/post_detail.html')
        )
        cls.private_templates = (
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}),
                'posts/create_post.html')
        )

    def form_asserts(self, post_object):
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.author, self.post.author)
        self.assertEqual(post_object.group, self.post.group)
        self.assertEqual(post_object.image, self.post.image)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

# Проверка используемых шаблонов
    def test_public_pages_use_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон на публичных страницах.
        """
        for reverse_name, template in self.public_templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_private_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон на персональных страницах.
        """
        for reverse_name, template in self.private_templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

# Проверка передаваемого контекста
    def test_public_pages_context(self):
        """Шаблоны index, group_post, post_detail и profile
        получают правильный context"""
        for reverse_name, _ in self.public_templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                if 'post' in response.context:
                    post_object = response.context.get('post')
                else:
                    post_object = response.context['page_obj'][0]
                self.form_asserts(post_object)

    def test_post_create_and_edit_context(self):
        """
        Шаблоны post_create и post_edit получают в context правильные поля
        формы
        """
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
            ('image', forms.fields.ImageField)
        )
        for reverse_name, _ in self.private_templates:
            response = self.authorized_client.get(reverse_name)
            for field_name, expected in form_fields:
                with self.subTest(field_name=field_name):
                    form_field = (
                        response.context.get('form').fields.get(field_name)
                    )
                    self.assertIsInstance(form_field, expected)

    def test_post_edit_form_context(self):
        """Шаблон post_edit получает правильные поля существующего поста"""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': self.post.id})))
        post_object = response.context.get('post')
        self.form_asserts(post_object)


# Проверка пагинации
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([Post(
            author=cls.user,
            text=f'Тестовый пост {i}',
            group=cls.group,
        )
            for i in range(POSTS_ON_1ST_PAGE + POSTS_ON_2ND_PAGE)
        ])
        cls.pagination_urls = (
            (reverse('posts:index')),
            (reverse('posts:group_list', kwargs={'slug': cls.group.slug})),
            (reverse('posts:profile', kwargs={'username': cls.user})),
        )
        cls.guest_client = Client()

    def test_pagination(self):
        """Паджинация корректно работает на всех страницах"""
        pages = (
            (1, POSTS_ON_1ST_PAGE),
            (2, POSTS_ON_2ND_PAGE),
        )
        for page, count in pages:
            for url in self.pagination_urls:
                with self.subTest(url=url):
                    response = self.client.get(url, {"page": page})
                    self.assertEqual(
                        len(response.context["page_obj"].object_list), count
                    )


# Проверка работы кеширования
class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_index_cache(self):
        """Проверка работы кеширования на главной странице"""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        request_1 = response_1.content
        post_info = Post.objects.get(id=1)
        post_info.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        request_2 = response_2.content
        self.assertTrue(request_1 == request_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        request_3 = response_3.content
        self.assertTrue(request_1 != request_3)


# Проверка работы подписок на пользователей
class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.user_1 = User.objects.create_user(username='TestUser1')
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        # Автор поста
        self.author_client = Client()
        self.author_client.force_login(self.author)
        # Пользователь, подписанный на автора
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)
        # Пользователь, не подписанный на автора
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписаться на автора"""
        count_follow = Follow.objects.count()
        self.authorized_client_1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author, self.author)
        self.assertEqual(follow.user, TestFollow.user_1)

    def test_profile_unfollow(self):
        """Авторизованный пользователь может отписаться от автора"""
        count_follow = Follow.objects.count()
        self.authorized_client_1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.authorized_client_1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_new_post_follow(self):
        """
        Посты появляются в ленте подписанных пользователей
        """
        count_follow = Follow.objects.filter(user=self.user_1).count()
        self.authorized_client_1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TestFollow.author.username}
            )
        )
        Post.objects.create(
            author=self.author,
            text='Тестовый пост 2',
            group=self.group
        )
        count_follow_new_post = Follow.objects.filter(user=self.user_1).count()
        self.assertEqual(count_follow_new_post, count_follow + 1)

    def test_new_post_not_follow(self):
        """
        Посты не появляются в ленте неподписанных пользователей
        """
        count_follow = Follow.objects.filter(user=self.user_1).count()
        self.authorized_client_1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TestFollow.author.username}
            )
        )
        Post.objects.create(
            author=self.author,
            text='Тестовый пост 3',
            group=self.group
        )
        self.authorized_client_1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        count_follow_new_post = Follow.objects.filter(user=self.user_1).count()
        self.assertNotEqual(count_follow_new_post, count_follow + 1)
