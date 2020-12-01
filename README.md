![randompantry](./randompantry.webp)

# Random Pantry

Random Pantry is a recipe recommender system that uses machine learning algorithms. It is designed to give you recipes that you will enjoy!

## Archived

randompantry will no longer be maintained. [randompantry3](https://github.com/irkaal/randompantry3) is a complete rewrite of randompantry in Python and TypeScript.

## Rating a Recipe

| Navigate to a recipe page through the popup window |  "Rate This Recipe!" is located after Tags |
| :-------------------------: | :-------------------------: |
| ![randompantry](./media/modal.png) | ![randompantry](./media/rate.png) |

## Getting Recommendations

| Recommendations are refreshed automatically whenever a new recipe is rated |
| :-------------------------: |
| ![randompantry](./media/recommendations.png) |

## Getting Similar Recipes

| Navigate to a recipe page | Similar Recipes can be found at the bottom |
| :------: | :----: |
| ![randompantry](./media/recipe-detail.png) | ![randompantry](./media/similar-recipes.png) |

## Data
* [Food.com Recipes and Interactions](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions) - Kaggle
* [Food.](https://www.food.com/) - Recipe Images

## Contributors
| [![irkules](https://avatars0.githubusercontent.com/u/55762386?s=400&v=4)](https://github.com/irkules) | [![deonnem](https://avatars3.githubusercontent.com/u/42830094?s=460&v=4)](https://github.com/deonnem) | [![irkaal](https://avatars0.githubusercontent.com/u/45277297?s=460&u=655fe8d05bb92cf2bad01027b304227e724a154b&v=4)](https://github.com/irkaal) |
| :-: | :-: | :-: |
| [`irkules`](http://github.com/irkules) | [`deonnem`](http://github.com/deonnem) | [`irkaal`](http://github.com/irkaal) |

## Changes
- Version 1.0
    - Initial implementation of Random Pantry
- Version 2.0
    - Asynchronous Random Pantry with Celery and Honcho
    - Migration to Global User
    - Addition of Database Cache
    - Addition of RecipeNet (Experimental MLP Model)
- Latest
    - Disabled Redis and Celery to allow for hosting on Heroku Free Dyno.
    - Removed RecipeNet

## Reference Papers
- Francesco Ricci, Lior Rokach, Bracha Shapira, and Paul B. Kantor. Recommender Systems Handbook. 1st edition, 2010.
- Ruslan Salakhutdinov and Andriy Mnih. Probabilistic matrix factorization. 2008. URL: http://papers.nips.cc/paper/3208-probabilistic-matrix-factorization.pdf.
- Yehuda Koren. Factorization meets the neighborhood: a multifaceted collaborative filtering model. 2008. URL: http://www.cs.rochester.edu/twiki/pub/Main/HarpSeminar/Factorization_Meets_the_Neighborhood-_a_Multifaceted_Collaborative_Filtering_Model.pdf.
- Yehuda Koren, Robert Bell, and Chris Volinsky. Matrix factorization techniques for recommender systems. 2009.
