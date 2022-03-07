from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user}/', 'posts/profile.html'),
            (f'/posts/{PostsURLTests.post.id}/', 'posts/post_detail.html')
        )
        cls.private_urls = (
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{PostsURLTests.post.id}/edit/', 'posts/create_post.html')
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls_exist(self):
        """
        Публичные страницы доступны любому неавторизированному пользователю.
        """
        for url, _ in self.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_error_page_url_exists(self):
        """Страница /error_page доступна любому неавторизированному
        пользователю.
        """
        response = self.guest_client.get('/posts/unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_private_urls_exist(self):
        """
        Персональные страницы доступны только авторизированным пользователям.
        """
        for url, _ in self.private_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_uses_correct_template(self):
        """Публичные URL-адреса используют соответствующие шаблоны."""
        for url, template in self.public_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_private_urls_uses_correct_template(self):
        """Персональные URL-адреса используют соответствующие шаблоны."""
        for url, template in self.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
