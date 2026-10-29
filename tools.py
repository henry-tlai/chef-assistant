import db


def save_favorite(title: str, recipe: str) -> str:
    """Save a recipe to the user's favorites. Use this when the user asks to
    save, favorite, or keep a recipe. title is the dish name; recipe is the
    full recipe text, including ingredients and numbered steps."""
    db.save_favorite(title, recipe)
    return f"Saved '{title}' to favorites."


def list_favorites() -> str:
    """List the recipes the user has saved as favorites. Use this when the
    user asks what they've saved or wants to see their favorites."""
    rows = db.list_favorites()
    if not rows:
        return "No favorites saved yet."
    return "\n".join(f"{row_id}. {title}" for row_id, title in rows)

def get_favorite(favorite_id: int) -> str:
    """Loads the full recipe for one saved favorite recipe. Use this when the user wants to open a saved recipe. 
    For example, "lets cook number 2". Then the favorite_id is from the numbered list that list_favorites show"""
    row = db.get_favorite(favorite_id)
    if row is None:
        return f"No favorite found with number {favorite_id}. Double-check your favorites list!"
    title, recipe = row
    return f"{title}\n\n{recipe}"


TOOLS = {
    "save_favorite": save_favorite,
    "list_favorites": list_favorites,
}