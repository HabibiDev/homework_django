from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.forms.formsets import formset_factory
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from .models import Dish, Ingredient, IngredientInOrder, Order
from notes.models import Note
from django.views.generic import ListView, DetailView, DeleteView
from django.db.models import Q
from django.views import View
from .forms import (AddDishForm,
                    AddIngredientForm,
                    AddIngredientFormFormSet,
                    AddIngredientToOrderFormSet,
                    OrderForm)

# Create your views here.


class DishListView(ListView):

    model = Dish
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dish_list'] = Dish.objects.all()
        return context


class DishDetailView(DetailView):

    model = Dish
    template_name = 'dish_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DishDetailView, self).get_context_data(**kwargs)
        content_type = ContentType.objects.get_for_model(Dish)
        context['notes'] = Note.objects.filter(note_item__content_type=content_type)
        context['dishes'] = self.model.objects.all()
        context['dish'] = self.get_object()
        context['dishes_ingredients'] = self.get_object().ingredient.all()
        return context


class AddDishView(View):
    template_name = 'add_dish.html'

    def get(self, request, *args, **kwargs):
        form_dish = AddDishForm()
        form_ingredient = AddIngredientFormFormSet()
        context = {'form_dish': form_dish, 'form_ingredient': form_ingredient}
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form_dish = AddDishForm(request.POST)
        form_ingredient = AddIngredientFormFormSet(request.POST)
        context = {'form_dish': form_dish, 'form_ingredient': form_ingredient}
        if form_dish.is_valid():
            dish = form_dish.save(commit=False)
            dish.save()
            for form in form_ingredient:
                if form.is_valid():
                    ingredient = form.save(commit=False)
                    if ingredient.name != None and ingredient.weight != None:
                        ingredient.save()
                        dish.ingredient.add(ingredient)
                        dish.save()

            return redirect('coocking_book:dish_list')
        return render(self.request, self.template_name, context)


class UpdateDishView(View):

    template_name = 'update_dish.html'

    def get(self, request, *args, **kwargs):
        dish_object = get_object_or_404(Dish, pk=self.kwargs['dish_id'])
        ingredients = Ingredient.objects.filter(dishes=dish_object.id)
        context = {'form_dish': dish_object, 'ingredients': ingredients}
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        dish_object = get_object_or_404(Dish, pk=self.kwargs['dish_id'])
        ingredients = Ingredient.objects.filter(dishes=dish_object.id)
        dish_object.title = request.POST.get('title')
        dish_object.description = request.POST.get('description')

        for ingredient in ingredients:
            if not request.POST.get('{0}_is_active'.format(ingredient.name)):
                ingredient.delete()
            else:
                if request.POST.get(ingredient.name) != ingredient.name:
                    ingredient.name = request.POST.get(ingredient.name)
                if str(request.POST.get('{0}_weight'.format(ingredient.name))) != str(ingredient.weight):
                    ingredient.weight = float(request.POST.get(
                        '{0}_weight'.format(ingredient.name))[:-2])
            ingredient.save()
        dish_object.save()
        if 'add_ingredients' in request.POST:
            return redirect(reverse('coocking_book:add_ingredients', kwargs={'dish_id': dish_object.id}))
        elif 'add_note' in request.POST:
            return redirect(reverse('notes:add_notes_to_dish', kwargs={'dish_id': dish_object.id}))
        else:
            return redirect('coocking_book:dish_list')


class AddIngredientView(View):
    template_name = 'add_ingredients.html'

    def get(self, request, *args, **kwargs):
        dish_object = get_object_or_404(Dish, pk=self.kwargs['dish_id'])
        form_ingredient = AddIngredientFormFormSet()
        context = {'form_ingredient': form_ingredient,
                   'dish_object': dish_object}
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        dish_object = get_object_or_404(Dish, pk=self.kwargs['dish_id'])
        form_ingredient = AddIngredientFormFormSet(request.POST)
        context = {'form_ingredient': form_ingredient,
                   'dish_object': dish_object}
        for form in form_ingredient:
            if form.is_valid():
                ingredient = form.save(commit=False)
                if ingredient.name != None and ingredient.weight != None:
                    ingredient.save()
                    dish_object.ingredient.add(ingredient)
                    dish_object.save()
            return redirect(reverse('coocking_book:update_dish', kwargs={'dish_id': dish_object.id}))
        return render(self.request, self.template_name, context)


class DeleteDishView(SuccessMessageMixin, DeleteView):
    model = Dish
    template_name = 'dish_confirm_delete.html'
    success_url = reverse_lazy('coocking_book:dish_list')


class AddOrderView(View):
    template_name = 'add_order_list.html'

    def get(self, request, *args, **kwargs):
        order_dish = Dish.objects.get(id=self.kwargs['dish_id'])
        form_order = OrderForm()
        form_ingredient = AddIngredientToOrderFormSet(
            queryset=Ingredient.objects.filter(dishes=self.kwargs['dish_id']))
        context = {'form_order': form_order,
                   'order_dish': order_dish,
                   'form_ingredient': form_ingredient, }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        order_dish = Dish.objects.get(id=self.kwargs['dish_id'])
        form_order = OrderForm(request.POST)
        form_ingredient = AddIngredientToOrderFormSet(request.POST)
        context = {'form_order': form_order,
                   'order_dish': order_dish,
                   'form_ingredient': form_ingredient, }
        if form_order.is_valid():
            order = form_order.save(commit=False)
            order.save()
            order.dish = order_dish
            order.save()
            for form in form_ingredient:
                if form.is_valid():
                    ingredient = form.save(commit=False)
                    if ingredient.name != None and ingredient.weight != None:
                        order_ingredient = IngredientInOrder(
                            name=ingredient.name, weight=ingredient.weight)
                        order_ingredient.save()
                        order.ingredients.add(order_ingredient)
                        order.save()
            return redirect('coocking_book:dish_list')
        return render(self.request, self.template_name, context)


class OrderListView(ListView):

    model = Order
    template_name = 'order_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.all()
        return context


class OrderDetailView(DetailView):

    model = Order
    template_name = 'order_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        content_type = ContentType.objects.get_for_model(Order)
        context['notes'] = Note.objects.filter(note_item__content_type=content_type)
        context['orders'] = self.model.objects.all()
        context['order'] = self.get_object()
        context['order_ingredient'] = self.get_object().ingredients.all()
        return context


class SearchView(ListView):
    model = Dish
    template_name = 'search_result.html'

    def get_queryset(self):
        queryset = super(DishListView, self).get_queryset()
        q = self.request.GET.get("q")
        if q:
            return queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))
        return queryset
