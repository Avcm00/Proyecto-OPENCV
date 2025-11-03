# apps/recommendations/tests/test_rule_engine.py
import asyncio
import pytest
from apps.recomendations.adapters.ml.recommendation_engine import RuleBasedRecommendationEngine
from apps.recomendations.core.entities import HaircutStyle, BeardStyle

@pytest.mark.asyncio
async def test_engine_prefers_matching_face_shape():
    engine = RuleBasedRecommendationEngine()
    s1 = HaircutStyle.new(name="Style A", description="para oval", image_url=None, suitable_for_shapes=["oval"])
    s2 = HaircutStyle.new(name="Style B", description="no match", image_url=None, suitable_for_shapes=["cuadrada"])
    results = await engine.generate_recommendations([s1, s2], face_shape="oval", gender="male", hair_length="short", user_preferences={})
    # primero s1
    assert results[0].id == s1.id

@pytest.mark.asyncio
async def test_engine_respects_excludes():
    engine = RuleBasedRecommendationEngine()
    s1 = HaircutStyle.new(name="Funky Crop", description="", image_url=None, suitable_for_shapes=["oval"])
    s2 = HaircutStyle.new(name="Safe Cut", description="", image_url=None, suitable_for_shapes=["oval"])
    prefs = {"exclude": ["funky"]}
    results = await engine.generate_recommendations([s1, s2], face_shape="oval", gender="male", hair_length="short", user_preferences=prefs)
    # Funky Crop should be penalizado
    assert results[0].id == s2.id
