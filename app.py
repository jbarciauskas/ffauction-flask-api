#!python
from flask import abort, Flask, request
from ffauction.league import League
from ffauction.player import PlayerSet, PlayerPriceJsonEncoder
from ffauction.pricing import VBDModel, PriceModel
from ffauction.user_settings import UserSettings
import json

app = Flask(__name__)

DEFAULTS = {
    "num_teams": 12,
    "team_budget": 200,
    "bench": 6,
    "flex_type": "rb/wr/te",
    "starter_budget_pct": .88,
    "override_bench_allocation": {},
    "roster": {
        "qb": 1,
        "rb": 2,
        "wr": 2,
        "te": 1,
        "flex": 1,
        "team_def": 1,
        "k": 1
    },
    "scoring": {
        "passAtt": 0,
        "passComp": 0,
        "passYds": .04,
        "passTds": 4,
        "twoPts": 2,
        "sacks": 0,  # Yahoo default: 0
        "passInt": -1,  # Yahoo default: -1
        "rushAtt": 0,
        "rushYds": .1,
        "rushTds": 6,
        "rec": 0,  # PPR setting
        "recYds": .1,
        "recTds": 6,
        "fumbles": -2
    }
}


@app.route('/players', methods=['POST', 'GET'])
def get_players():
    settings_dict = DEFAULTS.copy()
    if request.json:
        settings_dict.update(request.json)
    user_settings = UserSettings(settings_dict)
    player_set = PlayerSet()
    league = League(user_settings, player_set)
    player_set.load_projection_stats_from_csv('/Users/jbarciauskas/Documents/fantasyfootball/projections-20170806-avg-cbs-yahoo-nfl-fftoday-fantasydata.csv')
    league.calc_projected_points()
    vbd_model = VBDModel()
    vbd_model.calc_vbd(league)
    price_model = PriceModel()
    price_model.calc_base_prices(league)
    return json.dumps(player_set.get_all(), cls=PlayerPriceJsonEncoder)


if __name__ == '__main__':
    app.run(debug=True)
