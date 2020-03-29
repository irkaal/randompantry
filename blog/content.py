from blog import db, tasks
from blog.models import Recipe
from blog.nearest_recipes import NearestRecipes, NearestRecipesBaseline
from blog.recommender import RecipeRecommender
from blog.redis import RECOMMENDED_KEY, FAVOURITES_KEY, MAKE_AGAIN_KEY, TOP_RATED_KEY
from django.core.cache import cache
from numpy import logical_and
from randompantry.settings import USE_CELERY
from statistics import mean


class Content:
    @staticmethod
    def get_recipes(ids=None, all_columns=False):
        if all_columns:
            recipes = db.get_recipes(recipe_ids=ids)
        else:
            recipes = db.get_recipes(recipe_ids=ids, columns=['id', 'name', 'description', 'img_url', 'rating'])
        for recipe in recipes:
            current_rating = round(recipe['rating'])
            recipe['rating'] = range(current_rating)
            recipe['rating_null'] = range(5 - current_rating)
        return recipes

class HomeContent(Content):
    @staticmethod
    def get_home_context():
        home = dict()
        home['make_again'] = HomeContent.get_make_again()
        home['top_rated'] = HomeContent.get_top_rated()
        home['recommended'] = HomeContent.get_recommended()
        return home

    @staticmethod
    def get_recommended():
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])       
        if RECOMMENDED_KEY in cache:
            recommended_ids = cache.get(RECOMMENDED_KEY)
            return HomeContent.get_recipes(recommended_ids)
        db_cache = db.get_home_cache(columns=['recommended'])
        if 'recommended' in db_cache:
            recommended_ids = db_cache['recommended']
            cache.set(RECOMMENDED_KEY, recommended_ids)
            return HomeContent.get_recipes(recommended_ids)
        recommended_ids = tasks.get_recommended_ids(reviews)
        cache.set(RECOMMENDED_KEY, recommended_ids)
        db.update_home_cache(columns=['recommended'], values=[recommended_ids])
        return HomeContent.get_recipes(recommended_ids)

    @staticmethod
    def get_make_again():
        if MAKE_AGAIN_KEY in cache:
            make_again_ids = cache.get(MAKE_AGAIN_KEY)
            return RecipeDetailContent.get_recipes(make_again_ids)
        db_cache = db.get_home_cache(columns=['make_again'])
        if 'make_again' in db_cache:
            make_again_ids = db_cache['make_again']
            cache.set(MAKE_AGAIN_KEY, make_again_ids)
            return RecipeDetailContent.get_recipes(make_again_ids)
        make_again = db.get_make_again()
        for recipe in make_again:
            current_rating = round(recipe['rating'])
            recipe['rating'] = range(current_rating)
            recipe['rating_null'] = range(5 - current_rating)
        make_again_ids = [recipe['id'] for recipe in make_again]
        cache.set(MAKE_AGAIN_KEY, make_again_ids)
        return RecipeDetailContent.get_recipes(make_again_ids)

    @staticmethod
    def get_top_rated():
        if TOP_RATED_KEY in cache:
            top_rated_ids = cache.get(TOP_RATED_KEY)
            return RecipeDetailContent.get_recipes(top_rated_ids)
        db_cache = db.get_home_cache(columns=['top_rated'])
        if 'top_rated' in db_cache:
            top_rated_ids = db_cache['top_rated']
            cache.set(TOP_RATED_KEY, top_rated_ids)
            return RecipeDetailContent.get_recipes(top_rated_ids)
        top_rated = db.get_top_rated()
        for recipe in top_rated:
            current_rating = round(recipe['rating'])
            recipe['rating'] = range(current_rating)
            recipe['rating_null'] = range(5 - current_rating)
        top_rated_ids = [recipe['id'] for recipe in top_rated]
        cache.set(TOP_RATED_KEY, top_rated_ids)
        return top_rated

class RecipeDetailContent(Content):
    @staticmethod
    def get_recipe_detail_context(recipe_id):
        # TODO: Make db method to retrieve recipe info
        recipes = RecipeDetailContent.get_recipes(all_columns=True)
        # Current Recipe Attributes
        matched_recipes = [recipe for recipe in recipes if recipe['id'] == recipe_id]
        if not matched_recipes:
            return None
        current_recipe = matched_recipes[0]
        current_recipe['description'] = current_recipe['description'].capitalize()
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
        current_recipe['has_rated'] = len(reviews[logical_and(reviews.user_id == 1, reviews.recipe_id == recipe_id)]) != 0
        ingredients = db.get_ingredients(ingredient_ids=current_recipe['ingredient_ids'])
        current_recipe['ingredients'] = [ingredient.capitalize() for ingredient in ingredients]
        current_recipe['tags'] = db.get_tags(tag_ids=current_recipe['tag_ids'])
        steps = []
        for step in current_recipe['steps']:
            if step[0] == "'":
                step = step[1:]
            if step[-1] == "'":
                step = step[:-1]
            steps.append(step.capitalize())
        current_recipe['steps'] = steps
        # Similar Recipes
        similar_rating_ids = current_recipe['similar_rating']
        similar_ingredient_ids = current_recipe['similar_ingredients']
        similar_tag_ids = current_recipe['similar_tags']
        similar_nutrition_ids = current_recipe['similar_nutrition']
        has_cached_ids = similar_rating_ids and similar_ingredient_ids and similar_tag_ids and similar_nutrition_ids
        if not has_cached_ids:
            similar_rating_ids = RecipeDetailContent.get_similar_rating_ids(recipe_id, reviews)
            similar_ingredient_ids = RecipeDetailContent.get_similar_ingredients_ids(recipe_id, recipes)
            similar_tag_ids = RecipeDetailContent.get_similar_tags_ids(recipe_id, recipes)
            similar_nutrition_ids = RecipeDetailContent.get_similar_nutrition_ids(recipe_id, recipes)
            db.update_recipe_cache(
                recipe_id=recipe_id,
                columns=['similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'],
                values=[similar_rating_ids, similar_ingredient_ids, similar_tag_ids, similar_rating_ids]
            )
        current_recipe['similar_rating'] = RecipeDetailContent.get_recipes(similar_rating_ids)
        current_recipe['similar_ingredients'] = RecipeDetailContent.get_recipes(similar_ingredient_ids)
        current_recipe['similar_tags'] = RecipeDetailContent.get_recipes(similar_tag_ids)
        current_recipe['similar_nutrition'] = RecipeDetailContent.get_recipes(similar_nutrition_ids)
        return current_recipe

    @staticmethod
    def get_recipe_rating(recipe_id, reviews):
        reviews = reviews[reviews.recipe_id == recipe_id]
        if len(reviews):
            mean_rating = round(mean(reviews.rating))
            rating = range(mean_rating)
            rating_null = range(5 - mean_rating)
            return rating, rating_null
        return [], []

    @staticmethod
    def get_similar_rating_ids(recipe_id, reviews):
        if (reviews.recipe_id != recipe_id).all():
            return []
        model = NearestRecipesBaseline(k=40)
        model.fit(reviews)
        return model.predict(recipe_id)

    @staticmethod
    def get_similar_ingredients_ids(recipe_id, recipes):
        model = NearestRecipes()
        ingredient_ids_list = [recipe['ingredient_ids'] for recipe in recipes]
        model.fit(ingredient_ids_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def get_similar_tags_ids(recipe_id, recipes):
        model = NearestRecipes()
        tag_ids_list = [recipe['tag_ids'] for recipe in recipes]
        model.fit(tag_ids_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def get_similar_nutrition_ids(recipe_id, recipes):
        model = NearestRecipes(reduce=False)
        nutrition_list = [recipe['nutrition'] for recipe in recipes]
        model.fit(nutrition_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def add_review(rating, review, recipe_id, user_id):
        cache.delete_many([RECOMMENDED_KEY, MAKE_AGAIN_KEY, TOP_RATED_KEY])
        if USE_CELERY:
            tasks.insert_review.delay(rating, review, recipe_id, user_id)
        else:
            tasks.insert_review(rating, review, recipe_id, user_id)
