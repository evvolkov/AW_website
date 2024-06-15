import uuid

from django.db import models

_MAX_NAME = 50
_MAX_PHONE = 20
_MAX_ADDRESS = 150
_MAX_FEEDBACK = 500
_MAX_LINK = 100
_DEFAULT_MAX = 150
_MAX_TRACK_NUM = 20
_MAX_LOGIN_PW = 50


class FAQ(models.Model):
    """
    FAQ table. Stores the pull of answers and questions for FAQ page
    """
    question = models.CharField(max_length=_DEFAULT_MAX)
    answer = models.TextField(blank=True, db_default='', default='К сожалению, на этот вопрос пока не поступило ответа :(')

    class Meta:
        # Random ordering for FAQ table
        ordering = ['?']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question


class UserFeedback(models.Model):
    """
    User feedback table. Stores user scores, feedback text, as well as feedback sources and administration replies
    """
    _FEEDBACK_TYPE = {
        0: "Удобство заказа",
        1: "Функционал сайта",
        2: "Качество выполнения заказа",
        3: "Обратная связь и доставка",
    }

    _FEEDBACK_SOURCE = {
        0: "Сайт",
        1: "Сторонний ресурс",
        2: "Telegram",
        3: "Whatsapp",
        4: "E-mail"
    }

    # Base rate indicators
    rate = models.SmallIntegerField(default=0, db_default=0, blank=True, help_text='Пожалуйста, оцените работу сервиса')
    text = models.TextField(default='', db_default='', help_text='Поделитесь впечатлениями о работе сервиса', blank=True, max_length=_MAX_FEEDBACK)

    # Reply sent by carpentry employee
    reply = models.TextField(default='', db_default='', blank=True, max_length=_MAX_FEEDBACK)

    # Source link (outer sources only, e.g. ya.ru/some_forum/some_comment)
    source_link = models.CharField(default='', db_default='', blank=True, max_length=_MAX_LINK)

    # Categorical descriptionm
    feedback_type = models.SmallIntegerField(default=0, db_default=0, choices=_FEEDBACK_TYPE)
    feedback_source = models.SmallIntegerField(default=0, db_default=0, choices=_FEEDBACK_SOURCE)

    # DB linkage
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=False, db_default=None)

    class Meta:
        # Lower rates with details first
        # ordering = ['rate', '-text']
        constraints = [
            models.CheckConstraint(check=(models.Q(rate__gte=0) | ~models.Q(text='')), name='empty_feedback')
        ]

        pass

    def __str__(self):
        return self.rate.__str__() + ": " + self.text.__str__()


class User(models.Model):
    """
    Base user info
    """
    _USER_GROUP = {
        0: "Администратор",
        1: "Сотрудник магазина",
        2: "Довольный клиент",
    }

    _DELIVERY_TYPE = {
        0: "Самовывоз",
        1: "СДЭК",
    }

    # Administrator info
    user_group = models.SmallIntegerField(default=2, db_default=2, choices=_USER_GROUP)
    registration_date = models.DateField(auto_now_add=True, editable=False)

    # Personal info fields
    name = models.CharField(max_length=_MAX_NAME)
    second_name = models.CharField(max_length=_MAX_NAME)
    last_name = models.CharField(max_length=_MAX_NAME)
    phone = models.CharField(max_length=_MAX_PHONE, help_text='Основной контактный номер')
    email = models.EmailField(help_text='Действующий адрес электронной почты')
    birthdate = models.DateField(blank=True)

    # Auth params
    login = models.CharField(max_length=_MAX_NAME)
    password = models.CharField(max_length=_MAX_NAME)

    # Possible delivery info
    pref_delivery_type = models.SmallIntegerField(default=0, db_default=0, blank=True, choices=_DELIVERY_TYPE)
    main_address = models.CharField(max_length=_MAX_ADDRESS, blank=True, default='', db_default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['login'], name='unique_login'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),

        ]

    def __str__(self):
        return self.name.__str__() + " " + self.second_name.__str__() + " " + self.last_name.__str__()


class Order(models.Model):
    """
    Base order info
    # TODO: check constraints on all dates
    # TODO: unify delivery types with User
    # TODO: total price (atm = agg by ProductList + price from Delivery)
    # TODO: add price counting
    """
    _DELIVERY_TYPE = {
        0: "Самовывоз",
        1: "СДЭК",
    }

    _ORDER_STATUS = {
        0: "Новый заказ",
        1: "На уточнении",
        2: "Ожидает оплаты",
        3: "В работе",
        4: "Передается в доставку",
        5: "В доставке",
        6: "Завершен",
    }

    # Additional ID generated for user
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Date fields indicating stages of completion
    registration_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(blank=True)
    done_date = models.DateTimeField(blank=True)
    received_date = models.DateTimeField(blank=True)

    # Additional fields
    delivery_type = models.SmallIntegerField(default=0, db_default=0, blank=True, choices=_DELIVERY_TYPE)
    description = models.TextField(blank=True, max_length=_MAX_FEEDBACK, default='', db_default='')

    # Product price
    price = models.FloatField(default=0, db_default=0)

    # DB linkage
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=False, db_default=None)
    delivery = models.OneToOneField("Delivery", on_delete=models.CASCADE, null=True, blank=False, db_default=None)

    def __str__(self):
        return self.order_id


class Delivery(models.Model):
    """
    Base delivery info
    """
    _CDEC_STATUS = {
        0: "Заказ покинул город отправления",
        1: "Заказ готов к выдаче",
        2: "Заказ вручен",
        3: "Заказ выдан на доставку курьеру",
        4: "Заказ не вручен",
    }

    # Additional ID generated for user
    delivery_id = models.CharField(max_length=_MAX_TRACK_NUM, unique=True)

    # Delivery address
    address = models.CharField(max_length=_MAX_ADDRESS, default='', db_default='')

    # Delivery status (expanded CDEC classification)
    status = models.SmallIntegerField(default=0, db_default=0, blank=True, choices=_CDEC_STATUS)

    # Additional comment for delivery
    description = models.TextField(blank=True, max_length=_MAX_FEEDBACK, default='', db_default='')

    # Delivery price
    price = models.FloatField(default=0, db_default=0)

    class Meta:
        verbose_name_plural = "Deliveries"

    def __str__(self):
        return self.delivery_id


class Product(models.Model):
    """
    Base product parameters
    """

    _MATERIAL = {
        0: "Дуб",
        1: "Орех",
        2: "Ясень",
        3: "Акация",
        4: "Каучуковое дерево",
        5: "Манговое дерево",
        6: "Бамбук",
    }

    _USE_TYPE = {
        0: "Разделочная доска",
        1: "Сервировочная доска",
        2: "Подставка",
    }

    # Dimensional characteristics
    length = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()

    # Additional features
    legs = models.BooleanField(default=False)
    handles = models.BooleanField(default=True)
    groove = models.BooleanField(default=False)

    # Flavours
    material = models.SmallIntegerField(default=0, db_default=0, choices=_MATERIAL)

    # Categorical description
    use_type = models.SmallIntegerField(default=0, db_default=0, choices=_USE_TYPE)

    def __str__(self):
        return self.use_type.__str__() + ", " + self.material.__str__()


class ProductList(models.Model):
    """
    Transitive entity for source many-to-many relation between order and product
    """
    number = models.SmallIntegerField(default=1, db_default=1)

    # DB linkage
    order = models.ForeignKey("Order", on_delete=models.CASCADE, db_default=None)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, db_default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_product_in_list')
        ]

        pass

    def __str__(self):
        return self.order.__str__() + " - " + self.product.__str__()