from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from shopping.models import AppUser, CartItem, Category, Product


@pytest.mark.django_db
class TestViews:

    @patch("shopping.forms.requests.get")
    def test_signup_post_valid(self, mock_get, client):
        mock_get.return_value.json.return_value = {
            "data": {"result": "deliverable"}}

        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "contact": "8292028200",
            "password": "password123",
            "address": "Indore",
        }
        response = client.post(reverse("signup"), data)
        assert response.status_code == 302

    @patch("shopping.forms.requests.get")
    def test_signup_post_duplicate_email(self, mock_get, client):
        mock_get.return_value.json.return_value = {
            "data": {"result": "deliverable"}}

        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        AppUser.objects.create(
            user=user,
            username="testuser",
            email="testuser@example.com",
            contact="1234567890",
            address="Test",
        )

        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "contact": "8292028200",
            "password": "password123",
            "address": "Indore",
        }

        response = client.post(reverse("signup"), data)
        response_text = response.content.decode("utf-8")

        assert "Email already exists" in response_text

    def test_login_get_view(self, client):
        response = client.get(reverse("user_login"))
        assert response.status_code == 200

    def test_login_post_valid(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="testuser", password="testpass"
        )
        AppUser.objects.create(
            user=user,
            username="testuser",
            email="test@example.com",
            contact="123",
            address="addr",
        )
        data = {"username": "testuser", "password": "testpass"}
        response = client.post(reverse("user_login"), data)
        assert response.status_code == 200

    def test_add_product_get(self, client):
        response = client.get(reverse("add_product"))
        assert response.status_code == 200

    def test_product_detail(self, client):
        category = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            name="Test Product",
            desc="Description",
            price=100,
            stock=10,
            image="test.jpg",
            category=category,
        )
        response = client.get(reverse("product_detail", args=[product.id]))
        assert "product" in response.context

    def test_product_by_category(self, client):
        category = Category.objects.create(name="Electronics")
        product1 = Product.objects.create(
            name="Product 1",
            desc="Description",
            price=100,
            stock=10,
            image="test.jpg",
            category=category,
        )
        product2 = Product.objects.create(
            name="Product 2",
            desc="Description",
            price=150,
            stock=5,
            image="test.jpg",
            category=category,
        )

        response = client.get(
            reverse("product_list_by_category", args=[category.id]))
        assert response.status_code == 200
        assert product1.name in str(response.content)
        assert product2.name in str(response.content)

    def test_user_profile_view(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="user1", password="pass123", email="u1@example.com"
        )
        app_user = AppUser.objects.create(
            user=user,
            username="user1",
            email="u1@example.com",
            contact="123",
            address="addr",
        )
        print(app_user)
        client.force_login(user)
        response = client.get(reverse("user_profile"))
        assert response.status_code == 200

    def test_update_profile_get(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="upuser", password="pass", email="up@example.com"
        )
        AppUser.objects.create(
            user=user,
            username="upuser",
            email="up@example.com",
            contact="123",
            address="addr",
        )
        client.force_login(user)
        response = client.get(reverse("update_profile"))
        assert response.status_code == 200

    def test_update_profile_post(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="upd", password="pass", email="upd@example.com"
        )
        AppUser.objects.create(
            user=user,
            username="upd",
            email="upd@example.com",
            contact="123",
            address="addr",
        )
        client.force_login(user)
        data = {
            "username": "updated",
            "contact": "99999",
            "address": "new addr",
            "email": "upd@example.com",
        }
        response = client.post(reverse("update_profile"), data)
        assert response.status_code == 302

    def test_add_to_cart(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="cartuser", password="pass", email="cu@example.com"
        )
        app_user = AppUser.objects.create(
            user=user,
            username="cartuser",
            email="cu@example.com",
            contact="123",
            address="addr",
        )
        product = Product.objects.create(
            name="Item",
            desc="Desc",
            price=10,
            stock=10,
            image="a.jpg",
            category=Category.objects.create(name="cat"),
        )
        client.force_login(user)
        response = client.get(reverse("add_to_cart", args=[product.id]))
        assert response.status_code == 302
        assert CartItem.objects.filter(user=app_user, product=product).exists()

    def test_view_cart(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="vcuser", password="pass", email="vc@example.com"
        )
        app_user = AppUser.objects.create(
            user=user,
            username="vcuser",
            email="vc@example.com",
            contact="123",
            address="addr",
        )
        product = Product.objects.create(
            name="Prod",
            desc="Desc",
            price=10,
            stock=5,
            image="img.jpg",
            category=Category.objects.create(name="c"),
        )
        CartItem.objects.create(user=app_user, product=product, quantity=2)
        client.force_login(user)
        response = client.get(reverse("view_cart"))
        assert response.status_code == 200
        assert "cart_items" in response.context

    def test_remove_cart_item(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="remuser", password="pass", email="rem@example.com"
        )
        app_user = AppUser.objects.create(
            user=user,
            username="remuser",
            email="rem@example.com",
            contact="123",
            address="addr",
        )
        product = Product.objects.create(
            name="ToRemove",
            desc="D",
            price=5,
            stock=3,
            image="x.jpg",
            category=Category.objects.create(name="c"),
        )
        item = CartItem.objects.create(
            user=app_user, product=product, quantity=1)
        print(item)
        client.force_login(user)
        response = client.get(reverse("remove_items", args=[product.id]))
        assert response.status_code == 302
        assert not CartItem.objects.filter(
            user=app_user, product=product).exists()

    def test_delete_account(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="deluser", password="pass", email="del@example.com"
        )
        AppUser.objects.create(
            user=user,
            username="deluser",
            email="del@example.com",
            contact="123",
            address="addr",
        )
        client.force_login(user)
        response = client.get(reverse("delete_account"))
        assert response.status_code == 302

    def test_logout_view(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="logoutuser", password="pass"
        )
        client.force_login(user)
        response = client.get(reverse("logout_view"))
        assert response.status_code == 302

    def test_show_product_search(self, client):
        category = Category.objects.create(name="searchcat")
        Product.objects.create(
            name="SearchedItem",
            desc="match",
            price=20,
            stock=3,
            image="img.jpg",
            category=category,
        )
        response = client.get(reverse("show_product"), {"search": "Searched"})
        assert response.status_code == 200
        assert b"SearchedItem" in response.content

    def test_buy_now_page(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="buy", password="pass", email="buy@example.com"
        )
        app_user = AppUser.objects.create(
            user=user,
            username="buy",
            email="buy@example.com",
            contact="123",
            address="addr",
        )
        print(app_user)
        product = Product.objects.create(
            name="BuyItem",
            desc="Desc",
            price=99,
            stock=10,
            image="z.jpg",
            category=Category.objects.create(name="cat"),
        )
        client.force_login(user)
        response = client.get(reverse("buy_now", args=[product.id]))
        assert response.status_code == 200
