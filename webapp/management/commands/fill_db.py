from django.core.management.base import BaseCommand
from webapp import models


class Command(BaseCommand):
    help = 'Fill the database with the initial data'

    def handle(self, *args, **kwargs):
        faqs = [
            {'question': 'Какими способами осуществляется доставка?',
             'answer': 'На текущий момент Axiom Wood предоставляет 2 возможных опции для доставки: самовывоз и доставкой силами СДЭК (как в пункт выдачи, так и на дом).'},
            {'question': 'Какие изделия изготавливает ваша мастерская?',
             'answer': 'Наша мастерская изготавливает различные изделия из древесины. Axiom Wood специализируется на изготовлении небольших предметов, а основным направлением являются кухонные доски. В галерее нашего сайта Вы можете подробнее ознакомиться с вариантами возможных изделий.',},
            {'question': 'Когда закончатся работы на сайте?'},
            {'question': 'Почему сайт такой убогий?',
             'answer': 'К сожалению, он еще в разработке'},

        ]

        users = [
            {
                'name': 'Admin',
                'second_name': 'Admin',
                'last_name': 'Admin',
                'phone': '89876543210',
                'email': 'admin@mail.ru',
                'username': 'admin',
                'password': 'admin',
                'pref_delivery_type': -1,
                'user_group': 0
            },
            {
                'name': 'Ефросинья',
                'second_name': 'Агафьевна',
                'last_name': 'Иванова',
                'phone': '88005553535',
                'email': '88005553535@mail.ru',
                'birthdate': '1953-02-16',
                'username': 'Agafrosya',
                'password': '88005553535',
                'pref_delivery_type': 1,
                'main_address': 'г. Москва, ул. Пушкина, д. 42, кв. 69'
            },
            {
                'name': 'Валерий',
                'second_name': 'Секондович',
                'last_name': 'Павловский',
                'phone': '89261234567',
                'email': '89261234567@mail.ru',
                'birthdate': '1969-09-13',
                'username': 'Nastalo_moe_vremya',
                'password': 'Valera_reshala',
                'pref_delivery_type': 0,
                'main_address': ''
            },
            {
                'name': 'Усердный',
                'second_name': 'Сотрудник',
                'last_name': 'Мастерской',
                'phone': '89060358025',
                'email': 'somebody_once_told_me@mail.ru',
                'username': 'the_world_is_gonna',
                'password': 'roll_me',
                'pref_delivery_type': -1,
                'user_group': 1
            },
            {
                'name': 'Евгений',
                'second_name': 'Александрович',
                'last_name': 'Волков',
                'phone': '89154015847',
                'email': 'john@yandex.ru',
                'birthdate': '1996-05-07',
                'username': 'john',
                'password': 'sdam_psp_pozhe',
                'pref_delivery_type': -1,
                'user_group': 1
            },
        ]

        deliveries = [
            {
                'delivery_id': 'CDEC-12345',
                'address': 'с. Лох, Саратовская обл., ул. Пушкина, д. Колотушкина',
                'status': 2,
                'price': 666
            },
        ]

        for qa in faqs:
            question, created = models.FAQ.objects.get_or_create(**qa)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created question: {question}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Question is already created: {question}'))

        user_objs = {}
        for user_data in users:
            user, created = models.User.objects.get_or_create(**user_data)
            if user.__str__() == 'Иванова Ефросинья Агафьевна':
                user_objs['Иванова Ефросинья Агафьевна'] = user
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {user}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User is already created: {user}'))

        delivery_objs = {}
        for delivery_data in deliveries:
            delivery, created = models.Delivery.objects.get_or_create(**delivery_data)
            if delivery.__str__() == 'CDEC-12345':
                delivery_objs['CDEC-12345'] = delivery
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created delivery: {delivery}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Delivery is already created: {delivery}'))

        orders = [
            {
                'delivery_type': 1,
                'description': 'Тут описание самого успешного заказа, да еще и с доставкой!',
                'price': 2345.69,
                'user': user_objs['Иванова Ефросинья Агафьевна'],
                'status': 6,
                'delivery': delivery_objs['CDEC-12345'],
            },
            {
                'delivery_type': 0,
                'description': '',
                'price': 4000,
                'user': user_objs['Иванова Ефросинья Агафьевна'],
                'status': 3,
            },

        ]

        order_objs = {}
        for order_data in orders:
            order, created = models.Order.objects.get_or_create(**order_data)
            order_objs[order.id] = order
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created order: {order}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Order is already created: {order}'))

        products = [
            {
                'length': 450,
                'width': 350,
                'height': 50,
                'material': 0,
                'use_type': 0
            },
            {
                'length': 500,
                'width': 300,
                'height': 60,
                'material': 0,
                'use_type': 0,
                'legs': True,
                'groove': True
            },
            {
                'length': 350,
                'width': 200,
                'height': 15,
                'material': 5,
                'use_type': 1,
                'handles': False
            }
        ]

        product_objs = {}
        for product_data in products:
            product, created = models.Product.objects.get_or_create(**product_data)
            product_objs[product.id] = product
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Product is already created: {product}'))

        product_indx = list(product_objs.keys())
        order_indx = list(order_objs.keys())
        product_lists = [
            {
                'number': 1,
                'product': product_objs[product_indx[0]],
                'order': order_objs[order_indx[0]]
            },
            {
                'number': 2,
                'product': product_objs[product_indx[1]],
                'order': order_objs[order_indx[1]]
            },
            {
                'number': 1,
                'product': product_objs[product_indx[2]],
                'order': order_objs[order_indx[1]]
            },
        ]

        for product_list_data in product_lists:
            product_list, created = models.ProductList.objects.get_or_create(**product_list_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product list: {product_list}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Product list is already created: {product_list}'))

        feedbacks = [
            {
                'rate': 5,
                'text': 'Тамада хороший, и конкурсы интересные',
                'reply': 'Благодарим за тёплые слова!',
                'feedback_type': 2,
                'user': user_objs['Иванова Ефросинья Агафьевна'],
            },
            {
                'text': 'Вроде норм',
                'feedback_source': 2,
                'feedback_type': 3,
            },
        ]

        for feedback_data in feedbacks:
            user_feedback, created = models.UserFeedback.objects.get_or_create(**feedback_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user feedback: {user_feedback}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User feedback is already created: {user_feedback}'))


if __name__ == "__main__":
    pass