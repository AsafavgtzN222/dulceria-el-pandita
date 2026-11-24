from django import forms


ENTREGA_CHOICES = [
    ('', '— Selecciona una opción —'),
    ('Recoger en tienda', '🏪 Recoger en tienda (Col. San Juan, Xicoténcatl)'),
    ('Envío a domicilio', '🚚 Envío a domicilio (coordinar con nosotros)'),
]

PAGO_CHOICES = [
    ('transferencia', '🏦 Transferencia bancaria (SPEI en vivo)'),
    ('whatsapp', '💬 WhatsApp (coordinamos contigo)'),
    ('efectivo', '💵 Efectivo (al recoger en tienda)'),
]

BANCOS_CHOICES = [
    ('', '— Selecciona tu banco o app emisora —'),
    ('BBVA México', 'BBVA México'),
    ('Santander', 'Santander México'),
    ('Banorte', 'Banorte'),
    ('Citibanamex', 'Citibanamex'),
    ('Nu México', 'Nu México (Cuenta Nu)'),
    ('Mercado Pago', 'Mercado Pago Wallet'),
    ('Banco Azteca', 'Banco Azteca'),
    ('HSBC', 'HSBC México'),
    ('Scotiabank', 'Scotiabank'),
    ('Spin by OXXO', 'Spin by OXXO'),
    ('Inbursa', 'Banco Inbursa'),
    ('Hey Banco', 'Hey Banco'),
    ('Otro banco', 'Otro banco / Institución SPEI'),
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
    
    # Campos dinámicos para Transferencia bancaria
    banco_origen = forms.ChoiceField(
        choices=BANCOS_CHOICES,
        label='Banco emisor de la transferencia',
        required=False,
        widget=forms.Select(attrs={'class': 'campo-banco-select'}),
    )
    titular_transferencia = forms.CharField(
        max_length=100,
        label='Nombre del titular de la cuenta emisora',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Asaf Ávila Gutiérrez'}),
    )
    cuenta_digitos = forms.CharField(
        max_length=30,
        label='Número de cuenta o últimos dígitos',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 4152 3131 o terminación 9821', 'maxlength': '24'}),
    )
    folio_transferencia = forms.CharField(
        max_length=50,
        label='Folio de autorización o Clave de rastreo SPEI',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 072918 o MBAN010023...', 'maxlength': '40'}),
    )

    notas = forms.CharField(
        label='Notas del pedido',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Alergias, sabores favoritos, fecha especial...',
            'class': 'form-notas-area',
        }),
    )

    def clean_entrega(self):
        value = self.cleaned_data.get('entrega')
        if not value:
            raise forms.ValidationError('Por favor selecciona cómo quieres recibir tu pedido.')
        return value
