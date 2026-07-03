"""
API Flask - Projet iHeart Radio Analytics
Expose les 12 requêtes MongoDB validées et testées dans mongosh.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017")
db = client["RADIO"]


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "database": "iheart_db"})


# ---------------------------------------------------------------
# 1. Radios ayant un format/genre particulier (ex: Country)
#    GET /api/stations/by-genre?genre=Country
# ---------------------------------------------------------------
@app.route("/api/stations/by-genre", methods=["GET"])
def stations_by_genre():
    genre = request.args.get("genre", "Country")
    result = list(db.stations.find({"genre": genre}, {"name": 1, "format": 1, "_id": 0}))
    return jsonify(result)


# ---------------------------------------------------------------
# 2. Morceaux les plus joués sur une station particulière
#    GET /api/stations/<station_name>/top-tracks?limit=10
# ---------------------------------------------------------------
@app.route("/api/stations/<station_name>/top-tracks", methods=["GET"])
def top_tracks_for_station(station_name):
    limit = int(request.args.get("limit", 10))
    pipeline = [
        {"$match": {"name": station_name}},
        {"$lookup": {"from": "plays", "localField": "_id", "foreignField": "station_id", "as": "stationPlays"}},
        {"$unwind": "$stationPlays"},
        {"$group": {"_id": "$stationPlays.track_id", "playCount": {"$sum": 1}}},
        {"$sort": {"playCount": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "tracks", "localField": "_id", "foreignField": "_id", "as": "track"}},
        {"$unwind": "$track"},
        {"$project": {"_id": 0, "title": "$track.title", "album": "$track.album", "playCount": 1}},
    ]
    result = list(db.stations.aggregate(pipeline))
    if not result:
        return jsonify({"error": f"Aucun play trouvé pour la station '{station_name}'"}), 404
    return jsonify(result)


# ---------------------------------------------------------------
# 3. Genres dominants dans un état
#    GET /api/genres/by-state?state=CA
# ---------------------------------------------------------------
@app.route("/api/genres/by-state", methods=["GET"])
def genres_by_state():
    state = request.args.get("state", "CA")
    pipeline = [
        {"$lookup": {"from": "markets", "localField": "market_id", "foreignField": "_id", "as": "market"}},
        {"$unwind": "$market"},
        {"$match": {"market.state": state}},
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = list(db.stations.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 4. Artistes les plus diffusés dans un marché donné (ville)
#    GET /api/artists/by-city?city=Los Angeles&limit=10
# ---------------------------------------------------------------
@app.route("/api/artists/by-city", methods=["GET"])
def artists_by_city():
    city = request.args.get("city", "Los Angeles")
    limit = int(request.args.get("limit", 10))
    pipeline = [
        {"$lookup": {"from": "stations", "localField": "station_id", "foreignField": "_id", "as": "station"}},
        {"$unwind": "$station"},
        {"$lookup": {"from": "markets", "localField": "station.market_id", "foreignField": "_id", "as": "market"}},
        {"$unwind": "$market"},
        {"$match": {"market.city": city}},
        {"$lookup": {"from": "tracks", "localField": "track_id", "foreignField": "_id", "as": "track"}},
        {"$unwind": "$track"},
        {"$unwind": "$track.artist_ids"},
        {"$group": {"_id": "$track.artist_ids", "totalPlays": {"$sum": 1}, "city": {"$first": "$market.city"}}},
        {"$sort": {"totalPlays": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "artists", "localField": "_id", "foreignField": "_id", "as": "artist"}},
        {"$unwind": "$artist"},
        {"$project": {"_id": 0, "name": "$artist.name", "totalPlays": 1, "city": 1}},
    ]
    result = list(db.plays.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 5. Artistes associés à un track (recherche par titre)
#    GET /api/tracks/<title>/artists
# ---------------------------------------------------------------
@app.route("/api/tracks/<title>/artists", methods=["GET"])
def artists_of_track(title):
    pipeline = [
        {"$match": {"title": title}},
        {"$lookup": {"from": "artists", "localField": "artist_ids", "foreignField": "_id", "as": "artists"}},
        {"$project": {"_id": 0, "title": 1, "album": 1, "artists": "$artists.name"}},
    ]
    result = list(db.tracks.aggregate(pipeline))
    if not result:
        return jsonify({"error": f"Morceau '{title}' introuvable"}), 404
    return jsonify(result)


# ---------------------------------------------------------------
# 6. Stations avec le plus grand nombre de plays
#    GET /api/stations/top-plays?limit=10
# ---------------------------------------------------------------
@app.route("/api/stations/top-plays", methods=["GET"])
def stations_top_plays():
    limit = int(request.args.get("limit", 10))
    pipeline = [
        {"$group": {"_id": "$station_id", "totalPlays": {"$sum": 1}}},
        {"$sort": {"totalPlays": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "stations", "localField": "_id", "foreignField": "_id", "as": "station"}},
        {"$unwind": "$station"},
        {"$project": {
            "_id": 0,
            "call_letters": "$station.call_letters",
            "name": "$station.name",
            "format": "$station.format",
            "totalPlays": 1,
        }},
    ]
    result = list(db.plays.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 7. Quel état a le plus de stations actives (géographique uniquement)
#    GET /api/states/top-station-count
# ---------------------------------------------------------------
@app.route("/api/states/top-station-count", methods=["GET"])
def top_state_by_station_count():
    pipeline = [
        {"$lookup": {"from": "markets", "localField": "market_id", "foreignField": "_id", "as": "market"}},
        {"$unwind": "$market"},
        {"$match": {"market.state": {"$regex": r"^[A-Z]{2}$"}}},  # exclut "states/US-NAT" etc.
        {"$group": {"_id": "$market.state", "totalStations": {"$sum": 1}}},
        {"$sort": {"totalStations": -1}},
        {"$limit": 1},
    ]
    result = list(db.stations.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 8. Marchés sans aucune station d'un genre donné
#    GET /api/markets/without-genre?genre=Classic Rock
# ---------------------------------------------------------------
@app.route("/api/markets/without-genre", methods=["GET"])
def markets_without_genre():
    genre = request.args.get("genre", "Classic Rock")
    pipeline = [
        {"$lookup": {
            "from": "stations",
            "let": {"marketId": "$_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$market_id", "$$marketId"]}, "genre": genre}}
            ],
            "as": "stationsInGenre",
        }},
        {"$match": {"stationsInGenre": {"$size": 0}}},
        {"$project": {"_id": 0, "city": 1, "state": 1, "country": 1}},
    ]
    result = list(db.markets.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 9. Diversité de programmation par station (diversityRatio)
#    GET /api/stations/diversity?order=desc  (desc = plus variées, asc = plus répétitives)
# ---------------------------------------------------------------
@app.route("/api/stations/diversity", methods=["GET"])
def stations_diversity():
    order = -1 if request.args.get("order", "desc") == "desc" else 1
    limit = int(request.args.get("limit", 10))
    pipeline = [
        {"$group": {"_id": "$station_id", "totalPlays": {"$sum": 1}, "uniqueTracks": {"$addToSet": "$track_id"}}},
        {"$project": {
            "_id": 0,
            "station_id": "$_id",
            "totalPlays": 1,
            "diversityCount": {"$size": "$uniqueTracks"},
            "diversityRatio": {"$divide": [{"$size": "$uniqueTracks"}, "$totalPlays"]},
        }},
        {"$lookup": {"from": "stations", "localField": "station_id", "foreignField": "_id", "as": "station"}},
        {"$unwind": "$station"},
        {"$project": {
            "station_id": 1,
            "call_letters": "$station.call_letters",
            "format": "$station.format",
            "totalPlays": 1,
            "diversityCount": 1,
            "diversityRatio": 1,
        }},
        {"$sort": {"diversityRatio": order}},
        {"$limit": limit},
    ]
    result = list(db.plays.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 10. Artistes avec la plus forte audience globale
#     GET /api/artists/top-played?limit=10
# ---------------------------------------------------------------
@app.route("/api/artists/top-played", methods=["GET"])
def top_artists():
    limit = int(request.args.get("limit", 10))
    pipeline = [
        {"$lookup": {"from": "tracks", "localField": "track_id", "foreignField": "_id", "as": "track"}},
        {"$unwind": "$track"},
        {"$unwind": "$track.artist_ids"},
        {"$group": {"_id": "$track.artist_ids", "totalPlays": {"$sum": 1}}},
        {"$sort": {"totalPlays": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "artists", "localField": "_id", "foreignField": "_id", "as": "artist"}},
        {"$unwind": "$artist"},
        {"$project": {"_id": 0, "name": "$artist.name", "totalPlays": 1}},
    ]
    result = list(db.plays.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 11. Format générant le plus de plays (audience nationale mesurée)
#     GET /api/formats/top-plays
# ---------------------------------------------------------------
@app.route("/api/formats/top-plays", methods=["GET"])
def top_format_by_plays():
    pipeline = [
        {"$lookup": {"from": "stations", "localField": "station_id", "foreignField": "_id", "as": "station"}},
        {"$unwind": "$station"},
        {"$group": {"_id": "$station.format", "totalPlays": {"$sum": 1}}},
        {"$sort": {"totalPlays": -1}},
        {"$project": {"_id": 0, "format": "$_id", "totalPlays": 1}},
    ]
    result = list(db.plays.aggregate(pipeline))
    return jsonify(result)


# ---------------------------------------------------------------
# 12. Morceaux les plus longs / les plus courts
#     GET /api/tracks/duration-extremes?limit=5
# ---------------------------------------------------------------
@app.route("/api/tracks/duration-extremes", methods=["GET"])
def tracks_duration_extremes():
    limit = int(request.args.get("limit", 5))
    pipeline = [
        {"$facet": {
            "longest": [
                {"$sort": {"duration": -1}}, {"$limit": limit},
                {"$project": {"_id": 0, "title": 1, "duration": 1}},
            ],
            "shortest": [
                {"$sort": {"duration": 1}}, {"$limit": limit},
                {"$project": {"_id": 0, "title": 1, "duration": 1}},
            ],
        }}
    ]
    result = list(db.tracks.aggregate(pipeline))
    return jsonify(result[0] if result else {"longest": [], "shortest": []})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
