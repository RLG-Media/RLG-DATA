from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required

# Importing services
from invite import send_invite, resend_invite, delete_invite, accept_invite
from onlyfans_services import OnlyFansService
from discord_services import DiscordService
from snapchat_services import SnapchatService
from telegram_services import TelegramService
from twitch_services import TwitchService
from youtube_services import YouTubeService
from tiktok_services import TikTokService
from pinterest_services import PinterestService
from shopify_services import ShopifyService
from takealot_services import TakealotService
from messenger_services import MessengerService
from kick_services import KickService
from linkedin_services import LinkedInService
from aiemail_responseservices import AIEmailResponseService
from brandhealth_services import BrandHealthService
from contentplanning_services import ContentPlanningService
from contentscheduling_services import ContentSchedulingService
from crisismanagement_services import CrisisManagementService
from eventmonitoring_services import EventMonitoringService
from influencermatching_services import InfluencerMatchingService
from facebook_services import FacebookService
from instagram_services import InstagramService
from reddit_services import RedditService
from google_trends_services import GoogleTrendsService
from stripchat_services import StripchatService

# Importing the new services
from fanfix_services import FanfixService
from fansly_services import FanslyService
from fancentro_services import FanCentroService
from mym_services import MYMService
from fanvue_services import FanvueService
from ifans_services import IFansService
from fanso_services import FanSoService
from fantime_services import FanTimeService
from patreon_services import PatreonService
from unlocked_services import UnlockedService
from adultnode_services import AdultNodeService
from unfiltrd_services import UnfiltrdService
from flirtback_services import FlirtbackService
from admireme_services import AdmireMeService
from justforfans_services import JustForFansService
from manyvids_services import ManyVidsService
from scrileconnect_services import ScrileConnectService
from okfans_services import OkFansService
from fapello_services import FapelloService
from fansmetrics_services import FansmetricsService
from simpcity_services import SimpCityService
from avnstars_services import AVNStarsService

# Initialize services
onlyfans_service = OnlyFansService(user_token='YOUR_ONLYFANS_TOKEN')
discord_service = DiscordService(bot_token='YOUR_DISCORD_BOT_TOKEN')
snapchat_service = SnapchatService(access_token='YOUR_SNAPCHAT_ACCESS_TOKEN')
telegram_service = TelegramService(bot_token='YOUR_TELEGRAM_BOT_TOKEN')
twitch_service = TwitchService(client_id='YOUR_TWITCH_CLIENT_ID', access_token='YOUR_TWITCH_ACCESS_TOKEN')
youtube_service = YouTubeService(api_key='YOUR_YOUTUBE_API_KEY')
tiktok_service = TikTokService(access_token='YOUR_TIKTOK_ACCESS_TOKEN')
pinterest_service = PinterestService(access_token='YOUR_PINTEREST_ACCESS_TOKEN')
shopify_service = ShopifyService(access_token='YOUR_SHOPIFY_ACCESS_TOKEN')
takealot_service = TakealotService(api_key='YOUR_TAKEALOT_API_KEY')
messenger_service = MessengerService(page_access_token='YOUR_PAGE_ACCESS_TOKEN')
kick_service = KickService(access_token='YOUR_KICK_ACCESS_TOKEN')
linkedin_service = LinkedInService(access_token='YOUR_LINKEDIN_ACCESS_TOKEN')
ai_email_service = AIEmailResponseService(openai_api_key='YOUR_OPENAI_API_KEY')
brand_health_service = BrandHealthService(api_key='YOUR_BRAND_HEALTH_API_KEY')
content_planning_service = ContentPlanningService(api_key='YOUR_CONTENT_PLANNING_API_KEY')
content_scheduling_service = ContentSchedulingService(api_key='YOUR_CONTENT_SCHEDULING_API_KEY')
crisis_management_service = CrisisManagementService(api_key='YOUR_CRISIS_MANAGEMENT_API_KEY')
event_monitoring_service = EventMonitoringService(api_key='YOUR_EVENT_MONITORING_API_KEY')
influencer_matching_service = InfluencerMatchingService(api_key='YOUR_INFLUENCER_MATCHING_API_KEY')
facebook_service = FacebookService(access_token='YOUR_FACEBOOK_ACCESS_TOKEN')
instagram_service = InstagramService(access_token='YOUR_INSTAGRAM_ACCESS_TOKEN')
reddit_service = RedditService(client_id='YOUR_REDDIT_CLIENT_ID', client_secret='YOUR_REDDIT_SECRET', user_agent='YOUR_USER_AGENT')
google_trends_service = GoogleTrendsService()
stripchat_service = StripchatService(base_url='YOUR_STRIPCHAT_API_BASE_URL', api_key='YOUR_STRIPCHAT_API_KEY')

# Initialize the new services
fanfix_service = FanfixService(api_key='YOUR_FANFIX_API_KEY')
fansly_service = FanslyService(api_key='YOUR_FANSLY_API_KEY')
fancentro_service = FanCentroService(api_key='YOUR_FANCENTRO_API_KEY')
mym_service = MYMService(api_key='YOUR_MYM_API_KEY')
fanvue_service = FanvueService(api_key='YOUR_FANVUE_API_KEY')
ifans_service = IFansService(api_key='YOUR_IFANS_API_KEY')
fanso_service = FanSoService(api_key='YOUR_FANSO_API_KEY')
fantime_service = FanTimeService(api_key='YOUR_FANTIME_API_KEY')
patreon_service = PatreonService(api_key='YOUR_PATREON_API_KEY')
unlocked_service = UnlockedService(api_key='YOUR_UNLOCKED_API_KEY')
adultnode_service = AdultNodeService(api_key='YOUR_ADULTNODE_API_KEY')
unfiltrd_service = UnfiltrdService(api_key='YOUR_UNFILTRD_API_KEY')
flirtback_service = FlirtbackService(api_key='YOUR_FLIRTBACK_API_KEY')
admireme_service = AdmireMeService(api_key='YOUR_ADMIREME_API_KEY')
justforfans_service = JustForFansService(api_key='YOUR_JUSTFORFANS_API_KEY')
manyvids_service = ManyVidsService(api_key='YOUR_MANYVIDS_API_KEY')
scrileconnect_service = ScrileConnectService(api_key='YOUR_SCRILECONNECT_API_KEY')
okfans_service = OkFansService(api_key='YOUR_OKFANS_API_KEY')
fapello_service = FapelloService(api_key='YOUR_FAPELLO_API_KEY')
fansmetrics_service = FansmetricsService(api_key='YOUR_FANSMETRICS_API_KEY')
simpcity_service = SimpCityService(api_key='YOUR_SIMPCITY_API_KEY')
avnstars_service = AVNStarsService(api_key='YOUR_AVNSTARS_API_KEY')

# Define Blueprint for Routes
routes_blueprint = Blueprint('routes', __name__)

# ================== New Routes for Additional Services ==================
@routes_blueprint.route('/fanfix/fetch/<username>', methods=['GET'])
@login_required
def fetch_fanfix_data(username):
    data = fanfix_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fansly/fetch/<username>', methods=['GET'])
@login_required
def fetch_fansly_data(username):
    data = fansly_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fancentro/fetch/<username>', methods=['GET'])
@login_required
def fetch_fancentro_data(username):
    data = fancentro_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/mym/fetch/<username>', methods=['GET'])
@login_required
def fetch_mym_data(username):
    data = mym_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fanvue/fetch/<username>', methods=['GET'])
@login_required
def fetch_fanvue_data(username):
    data = fanvue_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/ifans/fetch/<username>', methods=['GET'])
@login_required
def fetch_ifans_data(username):
    data = ifans_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fanso/fetch/<username>', methods=['GET'])
@login_required
def fetch_fanso_data(username):
    data = fanso_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fantime/fetch/<username>', methods=['GET'])
@login_required
def fetch_fantime_data(username):
    data = fantime_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/patreon/fetch/<username>', methods=['GET'])
@login_required
def fetch_patreon_data(username):
    data = patreon_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/unlocked/fetch/<username>', methods=['GET'])
@login_required
def fetch_unlocked_data(username):
    data = unlocked_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/adultnode/fetch/<username>', methods=['GET'])
@login_required
def fetch_adultnode_data(username):
    data = adultnode_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/unfiltrd/fetch/<username>', methods=['GET'])
@login_required
def fetch_unfiltrd_data(username):
    data = unfiltrd_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/flirtback/fetch/<username>', methods=['GET'])
@login_required
def fetch_flirtback_data(username):
    data = flirtback_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/admireme/fetch/<username>', methods=['GET'])
@login_required
def fetch_admireme_data(username):
    data = admireme_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/justforfans/fetch/<username>', methods=['GET'])
@login_required
def fetch_justforfans_data(username):
    data = justforfans_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/manyvids/fetch/<username>', methods=['GET'])
@login_required
def fetch_manyvids_data(username):
    data = manyvids_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/scrileconnect/fetch/<username>', methods=['GET'])
@login_required
def fetch_scrileconnect_data(username):
    data = scrileconnect_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/okfans/fetch/<username>', methods=['GET'])
@login_required
def fetch_okfans_data(username):
    data = okfans_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fapello/fetch/<username>', methods=['GET'])
@login_required
def fetch_fapello_data(username):
    data = fapello_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/fansmetrics/fetch/<username>', methods=['GET'])
@login_required
def fetch_fansmetrics_data(username):
    data = fansmetrics_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/simpcity/fetch/<username>', methods=['GET'])
@login_required
def fetch_simpcity_data(username):
    data = simpcity_service.get_user_data(username)
    return jsonify(data)

@routes_blueprint.route('/avnstars/fetch/<username>', methods=['GET'])
@login_required
def fetch_avnstars_data(username):
    data = avnstars_service.get_user_data(username)
    return jsonify(data)

# ================== Continue with other routes ==================
