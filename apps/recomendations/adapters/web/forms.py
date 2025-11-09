from django import forms
from apps.recomendations.models import HaircutStyleModel, BeardStyleModel
import json

class HaircutStyleForm(forms.ModelForm):
    """Formulario para Estilos de Corte de Cabello"""
    
    # Campos personalizados para manejar JSONFields como texto
    suitable_for_shapes_text = forms.CharField(
        label='Formas de Rostro (separadas por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Ovalado, Redondo, Cuadrado'
        }),
        help_text='Lista de formas de rostro compatibles',
        required=False
    )
    
    suitable_for_gender_text = forms.CharField(
        label='Géneros Adecuados (separados por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Hombre, Mujer, Unisex'
        }),
        help_text='Lista de géneros compatibles',
        required=False
    )
    
    hair_length_required_text = forms.CharField(
        label='Longitudes de Cabello Requeridas (separadas por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Corto, Medio, Largo'
        }),
        help_text='Longitudes de cabello requeridas',
        required=False
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
            'image_url',
            'difficulty_level',
            'popularity_score',
            'is_active'
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
            'image_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://ejemplo.com/imagen.jpg'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select'
            }),
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
            self.fields['suitable_for_shapes_text'].initial = ', '.join(self.instance.suitable_for_shapes)
            self.fields['suitable_for_gender_text'].initial = ', '.join(self.instance.suitable_for_gender)
            self.fields['hair_length_required_text'].initial = ', '.join(self.instance.hair_length_required)
            self.fields['benefits_text'].initial = ', '.join(self.instance.benefits)
            self.fields['tags_text'].initial = ', '.join(self.instance.tags)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convertir campos de texto a listas para JSONField
        shapes = self.cleaned_data.get('suitable_for_shapes_text', '')
        instance.suitable_for_shapes = [s.strip() for s in shapes.split(',') if s.strip()]
        
        genders = self.cleaned_data.get('suitable_for_gender_text', '')
        instance.suitable_for_gender = [g.strip() for g in genders.split(',') if g.strip()]
        
        lengths = self.cleaned_data.get('hair_length_required_text', '')
        instance.hair_length_required = [l.strip() for l in lengths.split(',') if l.strip()]
        
        benefits = self.cleaned_data.get('benefits_text', '')
        instance.benefits = [b.strip() for b in benefits.split(',') if b.strip()]
        
        tags = self.cleaned_data.get('tags_text', '')
        instance.tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        if commit:
            instance.save()
        return instance


class BeardStyleForm(forms.ModelForm):
    """Formulario para Estilos de Barba"""
    
    # Campos personalizados para manejar JSONFields como texto
    suitable_for_shapes_text = forms.CharField(
        label='Formas de Rostro (separadas por coma)',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Ovalado, Redondo, Cuadrado'
        }),
        help_text='Lista de formas de rostro compatibles',
        required=False
    )
    
    benefits_text = forms.CharField(
        label='Beneficios (separados por coma)',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Ej: Define mandíbula, Añade masculinidad, Versátil',
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
        model = BeardStyleModel
        fields = [
            'name',
            'description',
            'image_url',
            'maintenance_level',
            'popularity_score',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Barba Completa'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Descripción detallada del estilo...',
                'rows': 4
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://ejemplo.com/imagen.jpg'
            }),
            'maintenance_level': forms.Select(attrs={
                'class': 'form-select'
            }),
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
            self.fields['suitable_for_shapes_text'].initial = ', '.join(self.instance.suitable_for_shapes)
            self.fields['benefits_text'].initial = ', '.join(self.instance.benefits)
            self.fields['tags_text'].initial = ', '.join(self.instance.tags)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convertir campos de texto a listas para JSONField
        shapes = self.cleaned_data.get('suitable_for_shapes_text', '')
        instance.suitable_for_shapes = [s.strip() for s in shapes.split(',') if s.strip()]
        
        benefits = self.cleaned_data.get('benefits_text', '')
        instance.benefits = [b.strip() for b in benefits.split(',') if b.strip()]
        
        tags = self.cleaned_data.get('tags_text', '')
        instance.tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        if commit:
            instance.save()
        return instance