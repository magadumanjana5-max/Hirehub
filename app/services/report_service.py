class ReportService:
    def build_report(self, jobs, applications):
        status_counts = {}
        for application in applications:
            status = application.get('status', 'applied')
            status_counts[status] = status_counts.get(status, 0) + 1
        return {
            'total_jobs': len(jobs),
            'total_applications': len(applications),
            'job_titles': [job.get('title') for job in jobs],
            'applications_by_status': status_counts,
        }
