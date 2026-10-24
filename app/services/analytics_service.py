from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    def dashboard(self):
        overview = self.repo.overview()
        if self.repo.database is not None:
            open_jobs = self.repo.database['jobs'].count_documents({'status': 'open'})
        else:
            jobs = self.repo.all()
            open_jobs = sum(1 for job in jobs if job.get('status') == 'open')
        overview['open_jobs'] = open_jobs
        return overview
