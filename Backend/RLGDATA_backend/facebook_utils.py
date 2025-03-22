import requests

def get_facebook_insights(page_id, access_token):
    url = f'https://graph.facebook.com/v12.0/{page_id}/insights'
    params = {
        'access_token': access_token,
        'metric': 'page_engaged_users,page_impressions',
        'period': 'day',
    }
    response = requests.get(url, params=params)
    return response.json()
