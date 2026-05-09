import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_key_here"

# Get current project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load recipes.json safely
with open(os.path.join(BASE_DIR, "recipes.json"), "r", encoding="utf-8") as f:
    recipes_data = json.load(f)


# Find matching recipes
def find_matching_recipes(user_ingredients):
    user_set = set([i.strip().lower() for i in user_ingredients])

    matched = []

    for recipe in recipes_data:
        recipe_ing_names = set(
            [x["name"].strip().lower() for x in recipe["ingredient_details"]]
        )

        have = recipe_ing_names & user_set
        missing = recipe_ing_names - user_set

        if have:
            matched.append({
                "recipe": recipe,
                "have_count": len(have),
                "missing_count": len(missing),
                "have_list": list(have),
                "missing_list": list(missing)
            })

    matched.sort(key=lambda x: x["have_count"], reverse=True)

    return matched


# Home Page
@app.route("/", methods=["GET"])
def home():
    saved = session.get("saved_recipes", [])

    return render_template(
        "index.html",
        saved_recipes=saved,
        recipes_data=recipes_data
    )


# Suggest Recipes
@app.route("/suggest-recipes", methods=["POST"])
def suggest_recipes():

    ingredients = request.form.get("ingredients", "")

    user_ingredients = [
        i.strip().lower()
        for i in ingredients.split(",")
        if i.strip()
    ]

    matched_recipes = find_matching_recipes(user_ingredients)

    # Save latest search
    session["last_search"] = user_ingredients

    return render_template(
        "results.html",
        suggestions=matched_recipes,
        user_ingredients=ingredients
    )


# Recipe Details Page
@app.route("/recipe/<name>", methods=["GET"])
def recipe_detail(name):

    recipe = next(
        (r for r in recipes_data if r["name"] == name),
        None
    )

    if not recipe:
        return "Recipe not found", 404

    user_ingredients = session.get("last_search", [])

    user_set = set(
        [i.strip().lower() for i in user_ingredients]
    )

    recipe_ing_names = set(
        [x["name"].strip().lower() for x in recipe["ingredient_details"]]
    )

    have = recipe_ing_names & user_set
    missing = recipe_ing_names - user_set

    return render_template(
        "preparation.html",
        recipe=recipe,
        have_count=len(have),
        missing_count=len(missing),
        have_list=list(have),
        missing_list=list(missing)
    )


# Save Recipe
@app.route("/save-recipe", methods=["POST"])
def save_recipe():

    recipe_name = request.form.get("recipe_name")

    if not recipe_name:
        return redirect(url_for("home"))

    saved = session.get("saved_recipes", [])

    if recipe_name not in saved:
        saved.append(recipe_name)

    session["saved_recipes"] = saved

    return redirect(url_for("home"))


# Run App
if __name__ == "__main__":
    app.run()
