from django import forms
from .models import Products


class ProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = [
            "category",
            "name",
            "description",
            "price",
            "stock",
            "is_available",
            "image",
        ]

        widgets = {
            "category": forms.Select(
                attrs={"class": "w-full border rounded-lg px-4 py-3"}
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-3",
                    "placeholder": "Enter product name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-3",
                    "rows": 4,
                    "placeholder": "Enter product description",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-3",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-3",
                    "min": "0",
                }
            ),
            "is_available": forms.CheckboxInput(attrs={"class": "w-5 h-5"}),
            "image": forms.ClearableFileInput(
                attrs={"class": "w-full border rounded-lg px-4 py-3"}
            ),
        }
