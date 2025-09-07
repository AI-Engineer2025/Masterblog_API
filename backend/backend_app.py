from flask import Flask, request, jsonify

app = Flask(__name__)

# Beispiel-Daten
POSTS = [
    {"id": 1, "title": "Hello World", "content": "This is my first post."},
    {"id": 2, "title": "Flask Tutorial", "content": "Learn Flask with me."},
    {"id": 3, "title": "Python Tips", "content": "Useful Python tricks."},
]


def sort_posts(posts, sort_field, direction):
    """
    Hilfsfunktion: Sortiert eine Liste von Posts nach einem Feld.

    :param posts: Liste der Posts (dicts)
    :param sort_field: Feldname zum Sortieren ('title' oder 'content')
    :param direction: 'asc' für aufsteigend, 'desc' für absteigend
    :return: Sortierte Liste (Original bleibt unverändert)
    """
    if sort_field not in {'title', 'content'}:
        return posts

    reverse = direction == 'desc'
    return sorted(
        posts,
        key=lambda post: post.get(sort_field, "").lower(),
        reverse=reverse
    )


def search_posts(posts, query):
    """
    Hilfsfunktion: Filtert Posts, die den Suchbegriff im Titel oder Inhalt enthalten.

    :param posts: Liste der Posts
    :param query: Suchbegriff (String)
    :return: Gefilterte Liste von Posts (kann leer sein)
    """
    if not query:
        return posts

    query_lower = query.lower()
    return [
        post for post in posts
        if query_lower in post.get("title", "").lower()
        or query_lower in post.get("content", "").lower()
    ]


@app.route('/api/posts', methods=['GET'])
def list_posts():
    """
    Listet alle Blogposts auf.
    Unterstützt optionale Query-Parameter:
      - ?sort=title|content
      - ?direction=asc|desc
      - ?search=Suchbegriff

    Ohne Parameter: Originalreihenfolge.
    Mit 'search': Filterung nach Titel oder Inhalt (leere Liste, wenn nichts gefunden).
    Mit 'sort' + 'direction': Sortierung (optional kombinierbar mit Suche).

    ✅ Erfolg: 200 OK (auch bei leerer Liste)
    """
    try:
        result_posts = POSTS.copy()

        # Suche anwenden
        search_query = request.args.get('search', '').strip()
        result_posts = search_posts(result_posts, search_query)

        # Sortierung anwenden
        sort_field = request.args.get('sort')
        direction = request.args.get('direction', 'asc')

        if sort_field:
            valid_directions = {'asc', 'desc'}
            if direction not in valid_directions:
                return jsonify({
                    "error": "Ungültige Sortierrichtung. Erlaubt: 'asc', 'desc'"
                }), 400
            result_posts = sort_posts(result_posts, sort_field, direction)

        return jsonify(result_posts), 200  # ✅ 200 OK auch bei leerer Liste

    except Exception as e:
        return jsonify({
            "error": "Interner Serverfehler",
            "details": str(e)
        }), 500


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Fügt einen neuen Blogpost hinzu.
    Erwartet JSON mit {"title": "...", "content": "..."}.
    Generiert automatisch eine eindeutige ID.

    ✅ Erfolg: 201 Created
    ❌ Fehler: 400 Bad Request, wenn title oder content fehlt
    """
    try:
        new_post = request.get_json()
        if not new_post:
            return jsonify({"error": "Keine Daten gesendet"}), 400

        missing_fields = []
        if "title" not in new_post:
            missing_fields.append("title")
        if "content" not in new_post:
            missing_fields.append("content")

        if missing_fields:
            return jsonify({
                "error": "Fehlende Pflichtfelder",
                "missing_fields": missing_fields
            }), 400  # ✅ 400 Bad Request bei fehlenden Feldern

        new_id = max((post["id"] for post in POSTS), default=0) + 1
        new_post["id"] = new_id

        POSTS.append(new_post)
        return jsonify(new_post), 201  # ✅ 201 Created (Standard für Ressourcen-Erstellung)

    except Exception as e:
        return jsonify({"error": "Interner Serverfehler", "details": str(e)}), 500


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Aktualisiert einen bestehenden Blogpost.
    Erwartet JSON mit den zu aktualisierenden Feldern.
    ID wird aus URL entnommen und darf nicht geändert werden.

    ✅ Erfolg: 200 OK → aktualisierter Post
    ❌ Fehler: 404 Not Found → wenn ID nicht existiert
    """
    try:
        updated_data = request.get_json()
        if not updated_data:
            return jsonify({"error": "Keine Daten gesendet"}), 400

        for post in POSTS:
            if post["id"] == post_id:
                for key, value in updated_data.items():
                    if key != "id":
                        post[key] = value
                return jsonify(post), 200  # ✅ 200 OK bei Erfolg

        # ❌ Kein Post mit dieser ID gefunden
        return jsonify({
            "error": "Post nicht gefunden",
            "message": f"Kein Post mit ID {post_id} vorhanden."
        }), 404  # ✅ 404 Not Found

    except Exception as e:
        return jsonify({
            "error": "Interner Serverfehler",
            "details": str(e)
        }), 500


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Löscht einen Blogpost anhand seiner ID.

    ✅ Erfolg: 200 OK → Bestätigungsnachricht
    ❌ Fehler: 404 Not Found → wenn ID nicht existiert
    """
    try:
        for i, post in enumerate(POSTS):
            if post["id"] == post_id:
                POSTS.pop(i)
                return jsonify({
                    "message": f"Post with id {post_id} has been deleted successfully."
                }), 200  # ✅ 200 OK bei Erfolg

        # ❌ Kein Post mit dieser ID gefunden
        return jsonify({
            "error": "Post nicht gefunden",
            "message": f"Kein Post mit ID {post_id} vorhanden."
        }), 404  # ✅ 404 Not Found

    except Exception as e:
        return jsonify({
            "error": "Interner Serverfehler",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)