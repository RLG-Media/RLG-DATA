from datetime import datetime, timedelta
from models import db, User, Platform, ContentData, TrendAnalysis, MonetizationStrategy, Campaign
from werkzeug.security import generate_password_hash

def seed_data():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create test users (creators and brands)
    user1 = User(username="creator_user", email="creator@example.com", password_hash=generate_password_hash("password123"), role="creator", subscription_status="active")
    user2 = User(username="brand_user", email="brand@example.com", password_hash=generate_password_hash("securepass456"), role="brand", subscription_status="active")

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # Seed platforms for each user
    platforms = [
        Platform(name="OnlyFans", creator_id=user1.id),
        Platform(name="Stripchat", creator_id=user1.id),
        Platform(name="Sheer", creator_id=user2.id),
        Platform(name="Patreon", creator_id=user2.id)
    ]

    db.session.bulk_save_objects(platforms)
    db.session.commit()

    # Seed Content Data for different platforms
    content_data_samples = [
        ContentData(platform_id=platforms[0].id, content_type="short-form", engagement_score=87.5, monetization_score=92.0, views=5000, likes=1200, comments=300, shares=150, posted_at=datetime.utcnow() - timedelta(days=2)),
        ContentData(platform_id=platforms[1].id, content_type="live-stream", engagement_score=78.0, monetization_score=88.5, views=8000, likes=900, comments=400, shares=200, posted_at=datetime.utcnow() - timedelta(days=1)),
        ContentData(platform_id=platforms[2].id, content_type="long-form", engagement_score=70.0, monetization_score=85.5, views=3000, likes=700, comments=100, shares=50, posted_at=datetime.utcnow() - timedelta(days=3)),
        ContentData(platform_id=platforms[3].id, content_type="short-form", engagement_score=82.0, monetization_score=90.0, views=10000, likes=1500, comments=500, shares=300, posted_at=datetime.utcnow())
    ]

    db.session.bulk_save_objects(content_data_samples)
    db.session.commit()

    # Seed trending topics for each platform
    trend_analyses = [
        TrendAnalysis(platform_id=platforms[0].id, keyword="exclusive content", trend_score=85.0, trend_analysis_report="Rising demand for exclusive content packages."),
        TrendAnalysis(platform_id=platforms[1].id, keyword="live streaming", trend_score=88.5, trend_analysis_report="Live streaming is highly engaging on this platform."),
        TrendAnalysis(platform_id=platforms[2].id, keyword="monthly subscriptions", trend_score=75.0, trend_analysis_report="Monthly subscriptions are trending due to affordability."),
        TrendAnalysis(platform_id=platforms[3].id, keyword="creator-driven content", trend_score=92.0, trend_analysis_report="Users prefer creator-driven content over sponsored posts.")
    ]

    db.session.bulk_save_objects(trend_analyses)
    db.session.commit()

    # Seed Monetization Strategies
    monetization_strategies = [
        MonetizationStrategy(platform_id=platforms[0].id, strategy_type="pricing", suggestion="Consider increasing subscription price by 5% for exclusive access", expected_impact=10.5),
        MonetizationStrategy(platform_id=platforms[1].id, strategy_type="content_format", suggestion="Introduce more live sessions during peak hours", expected_impact=12.0),
        MonetizationStrategy(platform_id=platforms[2].id, strategy_type="algorithm_optimization", suggestion="Optimize content for longer watch times", expected_impact=8.5),
        MonetizationStrategy(platform_id=platforms[3].id, strategy_type="cross-platform promotion", suggestion="Promote content through social media channels to increase traffic", expected_impact=15.0)
    ]

    db.session.bulk_save_objects(monetization_strategies)
    db.session.commit()

    # Seed campaigns for brands
    campaigns = [
        Campaign(user_id=user2.id, title="Holiday Special", description="Drive engagement through exclusive holiday offers", start_date=datetime.utcnow() - timedelta(days=10), end_date=datetime.utcnow() + timedelta(days=20), total_engagement=5000, total_revenue=15000),
        Campaign(user_id=user2.id, title="New Year Boost", description="Increase visibility for new year promotions", start_date=datetime.utcnow() - timedelta(days=5), total_engagement=3000, total_revenue=10000)
    ]

    db.session.bulk_save_objects(campaigns)
    db.session.commit()

    print("Database seeded with initial data.")

if __name__ == "__main__":
    seed_data()
