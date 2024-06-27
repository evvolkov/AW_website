from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FAQ, Order, User, UserFeedback, Product, Delivery, ProductList
from .forms import FAQForm, ProductForm, OrderForm, UserUpdateForm, SignUpForm, LoginForm
from django.forms import formset_factory
from django.http import JsonResponse

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import Group
import random
import time

# TODO: fix delivery price
_DEFAULT_PRICE = 666


def index(request):
    # TODO: add logo
    # TODO: add button 'наверх' instead of link
    # TODO: change policy and terms links
    # TODO: make footer stay at the bottom of the page
    # TODO: deal with footer svg (center)
    # TODO: navbar fix
    return render(request, 'webapp/index.html')


def gallery(request):
    # Sample photos context; replace with actual photo context
    photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
    return render(request, 'webapp/gallery.html', {'photos': photos})


def about(request):
    # Getting random top-3 FAQs to display on the page
    faqs = list(FAQ.objects.all())
    random.shuffle(faqs)
    faqs = faqs[:3]

    # Actions on submit button
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = FAQForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['text']
                if 'rate' not in request.POST:
                    rate = 0
                else:
                    rate = int(form.cleaned_data['rate'])

                if rate > 0 or text != '':
                    # TODO: user is unlinked to a feedback
                    feedback = UserFeedback(text=text, rate=rate, feedback_type=1, user=request.user)
                    feedback.save()
                    form.save()
                    error_msg = ''
                else:
                    error_msg = 'Пожалуйста, заполните форму обратной связи для отправки.'

                # TODO: change form for a success message
                return JsonResponse({'message_prefix': 'Спасибо за обратную связь!',
                                     'message_body': 'Мы приложим все усилия, чтобы улучшить наш сервис.',
                                     'message_error': error_msg})
        else:
            form = FAQForm()
            # TODO: login button here
            pass
    else:
        form = FAQForm()
    return render(request, 'webapp/about.html', {'faqs': faqs, 'form': form})


def order(request):
    # Redirect to profile page if the user is already authenticated
    # TODO: handle deleting the last and only form from a formset
    # TODO: fill forms with initials (change .empty_table -> <filled table>
    # TODO: resolve: forms hide on page reload
    if not request.user.is_authenticated:
        return redirect('profile')

    product_formset = formset_factory(ProductForm)

    formset = product_formset()
    order_form = OrderForm()

    if request.method == 'POST':
        tmp = request.POST

        # AJAX request processing
        if 'material' in request.POST and 'form-TOTAL_FORMS' not in request.POST:
            material = int(tmp.get('material', None))
            length = int(tmp.get('length', None))
            width = int(tmp.get('width', None))
            height = int(tmp.get('height', None))
            if tmp.get('handles', False) == 'false':
                handles = False
            else:
                handles = True
            if tmp.get('legs', False) == 'false':
                legs = False
            else:
                legs = True
            if tmp.get('groove', False) == 'false':
                groove = False
            else:
                groove = True
            number = int(tmp.get('number', None))
            price = float(tmp.get('price', '0.00'))

            # Any should be able or none
            # TODO: proper validation (including types) should be implemented
            if material is not None:
                # Response to ajax request
                res_price = Product.get_price(material=material, length=length, width=width, height=height,
                                              handles=handles,
                                              legs=legs, groove=groove, number=number, price=float(price))
                return JsonResponse({'text': f'{res_price:.2f}'})

        # AJAX request processing
        if 'delivery_type' in request.POST and 'form-TOTAL_FORMS' not in request.POST:
            delivery_type = tmp.get('delivery_type', None)
            address = tmp.get('address', None)

            # Mock for delivery price calculation
            # TODO: remove delivery price mock
            if delivery_type is not None:
                if delivery_type == '1':
                    delivery_price = '666.00'
                else:
                    delivery_price = '0.00'
                return JsonResponse({'text': delivery_price})

        formset = product_formset(request.POST)
        order_form = OrderForm(request.POST)

        # Here we go for the initial check meaning that the user only dealt with product list
        if formset.is_valid():
            for form in formset:
                form.submitted = True

            # product_forms = formset.save(commit=False)

            # if order_form.is_valid():
            #     order_form.submitted = True
            #
            # else:
            #     order_form.submitted = False
            #     # TODO: handle order_form errors
            #     pass

            # TODO: redirect to success page and save all data
            # TODO: success page = stage == 4 with reset of context so the next call will be a new order
            user = request.user
            # This time with saving to DB
            total_price = 0.
            product_instances = []
            numbers = []

            for indx, form in enumerate(formset):
                # TODO: proper form save
                product_attrs = {
                    'material': int(form.cleaned_data['material']),
                    'use_type': int(form.cleaned_data['use_type']),
                    'length': int(form.cleaned_data['length']),
                    'width': int(form.cleaned_data['width']),
                    'height': int(form.cleaned_data['height']),
                    'handles': bool(form.cleaned_data['handles']),
                    'legs': bool(form.cleaned_data['legs']),
                    'groove': bool(form.cleaned_data['groove']),
                    'price': float(request.POST.get(f'form-{indx}-price')) / float(form.cleaned_data['number'])
                }
                try:
                    product = Product.objects.get(**product_attrs)
                except Product.DoesNotExist as err:
                    product = Product(**product_attrs)

                # product = item.save()
                total_price += float(request.POST.get(f'form-{indx}-price'))
                numbers.append(int(form.cleaned_data['number']))

                # TODO: several identical products cause the error

                product.save()
                product_instances.append(product)

            delivery_type = int(request.POST.get('delivery_type'))
            order_attrs = {
                'description': request.POST.get('description', ''),
                'delivery_type': int(request.POST.get('delivery_type', 0)),
                'user': user,
                'delivery': None,
                'price': '0.00'
            }

            if delivery_type == 1:
                delivery = Delivery(address=request.POST.get('address', ''),
                                    description=request.POST.get('delivery_description'),
                                    price=float(request.POST.get('delivery_price')))
                delivery.save()
                order_attrs['delivery'] = delivery

            total_price += float(request.POST.get('delivery_price'))
            order_attrs['price'] = f'{total_price:.2f}'

            order_instance = Order(**order_attrs)
            order_instance.save()

            print(numbers)

            for indx, this_item in enumerate(product_instances):
                product_list = ProductList(product=this_item, order=order_instance, number=numbers[indx])
                product_list.save()

            return JsonResponse({'order_id': str(order_instance.order_id),
                                 'message_prefix': 'Ваш заказ успешно создан!',
                                 'message_body': 'Номер Вашего заказа: ',
                                 'message_suffix': 'Отследить статус заказа можно в личном кабинете.'})
            # return redirect('profile')
        else:
            formset.submitted = False
            # TODO: handle form errors
            pass

    elif request.method == 'GET':
        formset = product_formset(request.GET or None)
        for form in formset:
            price = Product.get_price(material=form.fields['material'].initial, length=form.fields['length'].initial,
                                      width=form.fields['width'].initial, height=form.fields['height'].initial,
                                      handles=form.fields['handles'].initial, legs=form.fields['legs'].initial,
                                      groove=form.fields['groove'].initial, number=form.fields['number'].initial,
                                      price=0.00)
            form.initial['price'] = f'{price:.2f}'
        order_form = OrderForm(request.GET or None)
        order_form.initial['delivery_price'] = '0.00'
        # Loading page for the first time, we've assigned initials earlier
        pass
    return render(request, 'webapp/order.html', {'formset': formset, 'order_form': order_form})


def profile(request):
    # Redirecting unauthorized users
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user

    if user.has_perm('webapp.all_orders_access'):
        # Stuff user -> full access
        user_orders = Order.objects.all()
    else:
        # Common user -> order history
        user_orders = Order.objects.filter(user=user)

    user_products = []
    total_products = 0
    total_orders = 0
    orders_in_progress = 0
    for order_instance in user_orders:
        total_orders += 1
        # TODO: count all statuses dynamically
        if getattr(order_instance, 'status') < 6:
            orders_in_progress += 1
        user_products.append({
            'order': order_instance,
            'products': ProductList.objects.filter(order=order_instance).select_related('product')
        })
        total_products += len(user_products[-1]['products'])

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'webapp/profile.html', {'form': form, 'orders': user_products, 'total_orders': total_orders, 'total_products': total_products, 'orders_in_progress': orders_in_progress})


def signup_view(request):
    # Redirect to profile page if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.errors:
            return render(request, 'webapp/signup.html', {'form': form})

        if form.is_valid():
            save_form = form.save(commit=False)
            save_form.set_password(form.cleaned_data.get('password'))

            user = User(username=save_form.username, password=save_form.password, name=save_form.name,
                        email=save_form.email, phone=save_form.phone, last_name=save_form.last_name)
            user.save()

            # Managing groups on sign up
            user_group = user.get_user_group(getattr(user, 'user_group'))
            group = Group.objects.get(name=user_group)
            group.user_set.add(user)
            group.save()
            user.groups.add(group)

            form.success = True
            login(request, user)
            # TODO: sleep is cringe
            time.sleep(3)
            return redirect('profile')
        else:
            return render(request, 'webapp/signup.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'webapp/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'webapp/login.html', {'form': form})


def logout_view(request):
    # TODO: something more elegant (e.g., suggestion to logout)
    # TODO: custom 404 page
    if not request.user.is_authenticated:
        return redirect('home')

    logout(request)
    return render(request, 'webapp/logout.html', {})


def policy(request):
    return render(request, 'webapp/policy.html', {})
