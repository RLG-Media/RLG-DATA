# routes.py - Main Routes for RLG Fans Application

from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from services.admireme_service import AdmireMeService
from services.adultnode_service import AdultNodeService
from services.avnstars_service import AVNStarsService
from services.fancentro_service import FanCentroService
from services.fanfix_service import FanfixService
from services.fansly_service import FanslyService
from services.fansmetrics_service import FansmetricsService
from services.fanso_service import FansoService
from services.fantime_service import FantimeService
from services.fanvue_service import FanvueService
from services.fapello_service import FapelloService
from services.flirtback_service import FlirtbackService
from services.ifans_service import IfansService
from services.justforfans_service import JustForFansService
from services.manyvids_service import ManyVidsService
from services.mym_service import MyMService
from services.okfans_service import OkFansService
from services.onlyfans_service import OnlyFansService
from services.patreon_service import PatreonService
from services.scrileconnect_service import ScrileConnectService
from services.simpcity_service import SimpCityService
from services.stripchat_service import StripChatService
from services.unfiltrd_service import UnfiltrdService
from services.unlocked_service import UnlockedService

# Initialize Blueprint
routes_blueprint = Blueprint('routes', __name__)

# Service Instances
onlyfans_service = OnlyFansService(api_key="ONLYFANS_API_KEY")
patreon_service = PatreonService(api_key="PATREON_API_KEY")
fansly_service = FanslyService(api_key="FANSLY_API_KEY")
fanfix_service = FanfixService(api_key="FANFIX_API_KEY")
fancentro_service = FanCentroService(api_key="FANCENTRO_API_KEY")
stripchat_service = StripChatService(api_key="STRIPCHAT_API_KEY")
# Other service instances here...

# ================== Route Definitions ==================

@routes_blueprint.route('/onlyfans/trending', methods=['GET'])
@login_required
def fetch_onlyfans_trending():
    trending_data = onlyfans_service.get_trending_content()
    return jsonify(trending_data)

@routes_blueprint.route('/fansly/popular', methods=['GET'])
@login_required
def fetch_fansly_popular():
    popular_data = fansly_service.get_popular_content()
    return jsonify(popular_data)

@routes_blueprint.route('/patreon/analytics', methods=['GET'])
@login_required
def fetch_patreon_analytics():
    analytics = patreon_service.get_user_analytics()
    return jsonify(analytics)

@routes_blueprint.route('/fanfix/content', methods=['POST'])
@login_required
def fetch_fanfix_content():
    data = request.json
    content = fanfix_service.search_content(data['keywords'])
    return jsonify(content)

@routes_blueprint.route('/fancentro/profile', methods=['GET'])
@login_required
def fetch_fancentro_profile():
    profile = fancentro_service.get_profile_data()
    return jsonify(profile)

@routes_blueprint.route('/stripchat/performers', methods=['GET'])
@login_required
def fetch_stripchat_performers():
    performers = stripchat_service.get_top_performers()
    return jsonify(performers)

@routes_blueprint.route('/admireme/insights', methods=['GET'])
@login_required
def fetch_admireme_insights():
    insights = AdmireMeService().get_insights()
    return jsonify(insights)

@routes_blueprint.route('/adultnode/engagement', methods=['POST'])
@login_required
def fetch_adultnode_engagement():
    data = request.json
    engagement = AdultNodeService().get_engagement_data(data['tags'])
    return jsonify(engagement)

@routes_blueprint.route('/avnstars/monetization', methods=['GET'])
@login_required
def fetch_avnstars_monetization():
    monetization_data = AVNStarsService().get_monetization_options()
    return jsonify(monetization_data)

# ================== Catch-All Error Handler ==================
@routes_blueprint.app_errorhandler(Exception)
def handle_exception(error):
    # Log error details
    error_details = str(error)
    print(f"Error: {error_details}")
    return jsonify({'error': 'An internal server error occurred.'}), 500
