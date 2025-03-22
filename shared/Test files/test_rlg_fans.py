import unittest
from app import create_app, db
from models import User, MonetizationStrategy, ContentRecommendation, BrandIntegration
from rlg_fans.monetization import generate_monetization_strategy
from rlg_fans.scraping import scrape_trending_content
from rlg_fans.recommendations import generate_content_recommendations
from rlg_fans.brands import find_brand_partnerships

class TestRLGFans(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the Flask app and set up the test database
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Create a test user
        cls.user = User(username="test_creator", email="creator@example.com")
        cls.user.set_password("password")
        db.session.add(cls.user)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up after tests
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_generate_monetization_strategy(self):
        """
        Test that a monetization strategy is generated based on user data.
        """
        strategy = generate_monetization_strategy(self.user.id, platform="OnlyFans", content_type="video")
        self.assertIsNotNone(strategy, "Monetization strategy was not generated.")
        self.assertIn("recommendations", strategy, "Strategy missing recommendations.")
        
        # Store the strategy in the database for further analysis
        new_strategy = MonetizationStrategy(user_id=self.user.id, strategy=strategy)
        db.session.add(new_strategy)
        db.session.commit()

        # Retrieve and verify saved strategy
        saved_strategy = MonetizationStrategy.query.filter_by(user_id=self.user.id).first()
        self.assertEqual(saved_strategy.strategy['platform'], "OnlyFans")

    def test_scrape_trending_content(self):
        """
        Test the scraping functionality for trending content.
        """
        platform = "Fansly"
        trending_content = scrape_trending_content(platform)
        
        # Check if content data was fetched successfully
        self.assertIsInstance(trending_content, list, "Trending content should be a list.")
        self.assertGreater(len(trending_content), 0, "No trending content found.")
        
        # Ensure each item in trending_content has necessary fields
        for item in trending_content:
            self.assertIn("title", item, "Missing title in scraped content.")
            self.assertIn("engagement", item, "Missing engagement in scraped content.")

    def test_generate_content_recommendations(self):
        """
        Test the generation of content recommendations for the user.
        """
        recommendations = generate_content_recommendations(self.user.id, platform="Fanvue")
        
        # Validate recommendations
        self.assertIsInstance(recommendations, list, "Recommendations should be a list.")
        self.assertGreater(len(recommendations), 0, "No recommendations generated.")
        
        # Store recommendations in the database
        for rec in recommendations:
            recommendation = ContentRecommendation(user_id=self.user.id, recommendation=rec)
            db.session.add(recommendation)
        db.session.commit()
        
        # Retrieve and verify saved recommendations
        saved_recommendations = ContentRecommendation.query.filter_by(user_id=self.user.id).all()
        self.assertGreater(len(saved_recommendations), 0, "Recommendations not saved in the database.")

    def test_find_brand_partnerships(self):
        """
        Test that brand partnerships are suggested based on creator content.
        """
        partnerships = find_brand_partnerships(self.user.id, content_type="photo")
        
        # Validate partnerships
        self.assertIsInstance(partnerships, list, "Partnerships should be a list.")
        self.assertGreater(len(partnerships), 0, "No brand partnerships found.")
        
        # Store partnerships in the database for record-keeping
        for partnership in partnerships:
            brand_integration = BrandIntegration(user_id=self.user.id, brand=partnership)
            db.session.add(brand_integration)
        db.session.commit()
        
        # Retrieve and validate saved partnerships
        saved_partnerships = BrandIntegration.query.filter_by(user_id=self.user.id).all()
        self.assertGreater(len(saved_partnerships), 0, "Brand partnerships not saved in the database.")
        self.assertIn("brand_name", saved_partnerships[0].brand, "Partnership missing brand name.")

if __name__ == '__main__':
    unittest.main()
