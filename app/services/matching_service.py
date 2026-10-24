class MatchingService:
    def match_jobs(self, candidate, jobs):
        if not candidate.get('skills'):
            return jobs[:3]
        skills = set(candidate.get('skills', []))
        scored = []
        for job in jobs:
            score = len(skills.intersection(job.get('requirements', [])))
            scored.append((score, job))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [job for _, job in scored[:5]]
