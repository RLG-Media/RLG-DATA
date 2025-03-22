import requests

def get_instagram_insights(account_id, access_token):
    url = f'https://graph.facebook.com/v12.0/{account_id}/insights'
    params = {
        'access_token': access_token,
        'metric': 'engagement,impressions,reach',
        'period': 'day',
    }
    response = requests.get(url, params=params)
    return response.json()
