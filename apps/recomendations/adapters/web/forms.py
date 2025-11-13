from django import forms
from apps.recomendations.models import HaircutStyleModel, BeardStyleModel, DIFFICULTY_CHOICES
import json
FACE_SHAPE_CHOICES = [
    ('oval', 'Ovalado'),
    ('redondo', 'Redondo'),
    ('cuadrado', 'Cuadrado'),
    ('corazon', 'Corazón'),
    ('diamante', 'Diamante'),
    ('triangular', 'Triangular'),
]

HAIR_LENGTH_CHOICES = [
    ('', 'Seleccione una longitud'), 
    ('corto', 'Corto'),
    ('medio', 'Medio'),
    ('largo', 'Largo'),
]

class HaircutStyleForm(forms.ModelForm):
    """Formulario para Estilos de Corte de Cabello"""
    
    # --- Campos de texto para JSONField ---
    suitable_for_shapes = forms.MultipleChoiceField( 
        label='Formas de Rostro Compatibles',
        choices=FACE_SHAPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            # ✅ CAMBIO CLAVE: Usar CheckboxSelectMultiple
            # Le asignamos una clase base que usaremos para seleccionar en JS
            'class': 'shape-checkboxes-group', 
        })
    )
    
    # ❌ ELIMINADO: suitable_for_gender_text (porque el modelo ahora usa el campo 'gender' CharField)
    # Si quieres que el usuario lo edite, solo usa el campo 'gender' normal del modelo.
    
    hair_length_required = forms.ChoiceField(
        label='Longitud de Cabello Requerida',
        choices=HAIR_LENGTH_CHOICES,
        required=True, # Debe elegir UNO
        widget=forms.Select(attrs={
            'class': 'form-select', # Renderiza un menú desplegable
        })
    )
    
    benefits_text = forms.CharField(
        label='Beneficios (separados por coma)',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Ej: Fácil de mantener, Versátil, Moderno',
            'rows': 3
        }),
        help_text='Beneficios del estilo',
        required=False
    )
    
    tags_text = forms.CharField(
        label='Etiquetas (separadas por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: clásico, moderno, elegante'
        }),
        help_text='Etiquetas del estilo',
        required=False
    )
    
    class Meta:
        model = HaircutStyleModel
        fields = [
            'name',
            'description',
            'gender', # 🆕 Agregado el campo 'gender' que es un CharField normal
            'image',  # 🔄 CORREGIDO: Usar 'image' en lugar de 'image_url'
            'difficulty_level',
            'popularity_score',
            'is_active',
            
            'benefits_text', 
            'tags_text',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Fade Clásico'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Descripción detallada del estilo...',
                'rows': 4
            }),
            # ❌ ELIMINADO: widget para 'image_url'
            # 'image': ImageInput (si deseas un widget específico, pero Django usa FileInput por defecto)
            'gender': forms.Select(attrs={ # 🆕 Widget para el campo 'gender' (Charfield)
                'class': 'form-select'
            }),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            
            'popularity_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 10,
                'step': 0.1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Rellenar campos de texto con datos del JSONField
            self.fields['suitable_for_shapes'].initial = self.instance.suitable_for_shapes
            self.fields['hair_length_required'].initial = self.instance.hair_length_required
            model_lengths = self.instance.hair_length_required
            if model_lengths:
                self.fields['hair_length_required'].initial = model_lengths[0]
            self.fields['benefits_text'].initial = ', '.join(self.instance.benefits)
            self.fields['tags_text'].initial = ', '.join(self.instance.tags)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convertir campos de texto a listas para JSONField
        instance.gender = self.cleaned_data.get('gender', instance.gender)
        instance.suitable_for_shapes = self.cleaned_data.get('suitable_for_shapes', [])     
        # ❌ ELIMINADO: Conversión de suitable_for_gender (manejo por campo 'gender' normal)
        
        length_str = self.cleaned_data.get('hair_length_required')
        if length_str:
            instance.hair_length_required = [length_str]
        else:
            instance.hair_length_required = []
        
        benefits = self.cleaned_data.get('benefits_text', '')
        instance.benefits = [b.strip() for b in benefits.split(',') if b.strip()]
        
        tags = self.cleaned_data.get('tags_text', '')
        instance.tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        if commit:
            instance.save()
        return instance
    
    
    
class BeardStyleForm(forms.ModelForm):
    """Formulario para Estilos de Barba"""

    suitable_for_shapes = forms.MultipleChoiceField(
        label='Formas de Rostro Compatibles',
        choices=FACE_SHAPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'shape-checkboxes-group space-y-1'
        })
    )

    benefits_text = forms.CharField(
        label='Beneficios (separados por coma)',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Ej: Define mandíbula, Añade masculinidad, Versátil',
            'rows': 3
        }),
        required=False
    )

    tags_text = forms.CharField(
        label='Etiquetas (separadas por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: clásico, moderno, elegante'
        }),
        required=False
    )

    difficulty_level = forms.ChoiceField(
        label='Nivel de Dificultad',
        choices=DIFFICULTY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = BeardStyleModel
        fields = [
            'name', 'description', 'image',
            'difficulty_level', 'popularity_score',
            'suitable_for_shapes',  # 👈 agrégalo aquí
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Barba Completa'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Descripción detallada del estilo...'
            }),
            'popularity_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 10,
                'step': 0.1
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['suitable_for_shapes'].initial = self.instance.suitable_for_shapes or []
            self.fields['benefits_text'].initial = ', '.join(self.instance.benefits or [])
            self.fields['tags_text'].initial = ', '.join(self.instance.tags or [])

    def save(self, commit=True):
        instance = super().save(commit=False)

        # ✅ Guardar lista de formas de rostro correctamente
        instance.suitable_for_shapes = self.cleaned_data.get('suitable_for_shapes', [])

        # ✅ Guardar beneficios y etiquetas
        benefits = self.cleaned_data.get('benefits_text', '')
        instance.benefits = [b.strip() for b in benefits.split(',') if b.strip()]

        tags = self.cleaned_data.get('tags_text', '')
        instance.tags = [t.strip() for t in tags.split(',') if t.strip()]

        if commit:
            instance.save()
        return instance
