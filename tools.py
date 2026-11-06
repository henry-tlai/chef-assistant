import db


def save_favorite(title: str, recipe: str) -> str:
    """Save a recipe to the user's favorites. Use this ONLY when the user's
    latest message explicitly asks to save, favorite, or keep a recipe. Never
    call this just because you wrote a recipe or the user said they liked it;
    offer to save it and wait for a yes instead. title is the dish name; recipe
    is the full recipe text, including ingredients and numbered steps."""
    db.save_favorite(title, recipe)
    return f"Saved '{title}' to favorites."


def list_favorites() -> str:
    """List the recipes the user has saved as favorites, by name. Use this when
    the user asks what they've saved or wants to see their favorites."""
    rows = db.list_favorites()
    if not rows:
        return "No favorites saved yet."
    return "\n".join(f"- {title}" for _, title in rows)


def get_favorite(title: str) -> str:
    """Load the full recipe for one saved favorite. Use this when the user wants
    to open, view, or cook a saved recipe, for example "let's cook the steak".
    title is the name of the recipe, or part of it, as the user said it."""
    matches = db.find_favorite(title)
    if not matches:
        return f"No favorite found matching '{title}'. Suggest the user check their favorites list."
    if matches:                                                 
        names = ", ".join(t for t, _ in matches)
        return f"Several favorites match: {names}. Ask the user which one they mean."
    found_title, recipe = matches                               
    return f"{found_title}\n\n{recipe}"


TOOLS = {
    "save_favorite": save_favorite,
    "list_favorites": list_favorites,
}