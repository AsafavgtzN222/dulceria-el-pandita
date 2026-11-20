from django import forms


ENTREGA_CHOICES = [
    ('', '— Selecciona una opción —'),
    ('Recoger en tienda', '🏪 Recoger en tienda (Col. San Juan, Xicoténcatl)'),
    ('Envío a domicilio', '🚚 Envío a domicilio (coordinar con nosotros)'),
]

PAGO_CHOICES = [
    ('transferencia', '🏦 Transferencia (SPEI / depósito)'),
    ('whatsapp', '💬 WhatsApp (coordinamos contigo)'),
    ('efectivo', '💵 Efectivo (al recoger en tienda)'),
]


class PedidoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre', 'required': True}),
    )
    apellido = forms.CharField(
        max_length=100,
        label='Apellido',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'}),
    )
    telefono = forms.CharField(
        max_length=20,
        label='WhatsApp / Teléfono',
        widget=forms.TextInput(attrs={'placeholder': '81 3712 2570', 'required': True}),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}),
    )
    entrega = forms.ChoiceField(
        choices=ENTREGA_CHOICES,
        label='¿Cómo quieres recibir tu pedido?',
    )
    direccion = forms.CharField(
        max_length=250,
        label='Dirección de entrega',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Calle, número, colonia, ciudad'}),
    )
    metodo_pago = forms.ChoiceField(
        choices=PAGO_CHOICES,
        label='Método de pago',
        widget=forms.RadioSelect,
    )
    notas = forms.CharField(
        label='Notas del pedido',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Alergias, sabores favoritos, fecha especial...',
            'style': 'min-height:80px;',
        }),
    )

    def clean_entrega(self):
        value = self.cleaned_data.get('entrega')
        if not value:
            raise forms.ValidationError('Por favor selecciona cómo quieres recibir tu pedido.')
        return value
