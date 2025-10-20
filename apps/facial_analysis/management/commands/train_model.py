# apps/facial_analysis/management/commands/train_model.py
from django.core.management.base import BaseCommand
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
from apps.facial_analysis.ml.image_loader import ImageLoader
from apps.facial_analysis.face_shape_detection import FaceShapeDetector
import os

class Command(BaseCommand):
    help = 'Entrena el modelo de clasificación de formas de rostro'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            default='dataset/faces',
            help='Ruta al directorio del dataset'
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Porcentaje de datos para test (0.2 = 20%)'
        )
    
    def handle(self, *args, **options):
        dataset_path = options['dataset']
        test_size = options['test_size']
        
        self.stdout.write(self.style.SUCCESS('\n========== ENTRENAMIENTO DE MODELO ==========\n'))
        
        # Validar dataset
        loader = ImageLoader(dataset_path)
        if not loader.validate_dataset_structure():
            self.stdout.write(self.style.ERROR('✗ Dataset inválido o incompleto'))
            return
        
        # Cargar imágenes
        self.stdout.write(self.style.SUCCESS('\n[1/3] Cargando imágenes...'))
        detector = FaceShapeDetector()
        X, y, loaded = loader.load_images_from_directory(detector)
        
        if loaded == 0:
            self.stdout.write(self.style.ERROR('✗ No se cargaron imágenes'))
            return
        
        # Entrenar modelo
        self.stdout.write(self.style.SUCCESS('\n[2/3] Entrenando modelo...'))
        classifier = FaceShapeClassifier()
        metrics = classifier.train(X, y, test_size=test_size)
        
        # Guardar modelo
        self.stdout.write(self.style.SUCCESS('\n[3/3] Guardando modelo...'))
        classifier.save_model()
        
        self.stdout.write(self.style.SUCCESS('\n✓ ¡Entrenamiento completado exitosamente!\n'))


# Script de uso rápido: scripts/train_quick.py
"""
Script rápido para entrenar sin Django
Ejecutar: python scripts/train_quick.py --dataset dataset/faces
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import numpy as np
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
from apps.facial_analysis.ml.image_loader import ImageLoader
from apps.facial_analysis.face_shape_detection import FaceShapeDetector

def main():
    parser = argparse.ArgumentParser(description='Entrenar modelo de clasificación facial')
    parser.add_argument('--dataset', type=str, default='dataset/faces',
                       help='Ruta al dataset')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Porcentaje de test')
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("   ENTRENAMIENTO MODELO FACE SHAPE")
    print("="*50 + "\n")
    
    # Cargar
    print(f"📂 Dataset: {args.dataset}")
    loader = ImageLoader(args.dataset)
    
    if not loader.validate_dataset_structure():
        print("\n✗ Error: Dataset inválido")
        return
    
    detector = FaceShapeDetector()
    X, y, loaded = loader.load_images_from_directory(detector)
    
    if loaded == 0:
        print("\n✗ Error: No se cargaron imágenes")
        return
    
    # Entrenar
    classifier = FaceShapeClassifier()
    classifier.train(X, y, test_size=args.test_size)
    classifier.save_model()
    
    print("\n✓ ¡Modelo entrenado y guardado!\n")

if __name__ == '__main__':
    main()