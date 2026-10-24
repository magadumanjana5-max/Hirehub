from app.services.matching_service import MatchingService


class RecommendationService:
    def __init__(self):
        self.matcher = MatchingService()

    def get_recommendations(self, candidate, jobs):
        return self.matcher.match_jobs(candidate, jobs)
