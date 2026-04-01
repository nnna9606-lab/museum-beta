"""Որոնման համակարգի օգնական ֆունկցիաներ"""
from sqlalchemy import or_
from datetime import datetime


def search_artifacts(query, filters=None):
    """Որոնել նմուշներ ըստ տրված հարցման և ֆիլտրերի"""
    from app import Artifact
    
    search = Artifact.query
    
    if query:
        search = search.filter(or_(
            Artifact.name.ilike(f'%{query}%'),
            Artifact.description.ilike(f'%{query}%'),
            Artifact.year.ilike(f'%{query}%')
        ))
    
    if filters:
        if 'year_from' in filters and filters['year_from']:
            search = search.filter(Artifact.year >= filters['year_from'])
        
        if 'year_to' in filters and filters['year_to']:
            search = search.filter(Artifact.year <= filters['year_to'])
            
        if 'category' in filters and filters['category']:
            search = search.filter(Artifact.category == filters['category'])
    
    # Return a list so callers/templates won't receive a Query object
    return search.order_by(Artifact.created_at.desc()).all()

def search_exhibitions(query, filters=None):
    """Որոնել ցուցադրություններ ըստ տրված հարցման և ֆիլտրերի"""
    from app import Exhibition
    
    search = Exhibition.query
    
    if query:
        search = search.filter(or_(
            Exhibition.title.ilike(f'%{query}%'),
            Exhibition.description.ilike(f'%{query}%')
        ))
    
    if filters:
        if 'date_from' in filters and filters['date_from']:
            search = search.filter(Exhibition.end_date >= filters['date_from'])
            
        if 'date_to' in filters and filters['date_to']:
            search = search.filter(Exhibition.start_date <= filters['date_to'])
            
        if 'status' in filters:
            today = datetime.now().date()
            if filters['status'] == 'active':
                search = search.filter(Exhibition.start_date <= today, Exhibition.end_date >= today)
            elif filters['status'] == 'upcoming':
                search = search.filter(Exhibition.start_date > today)
            elif filters['status'] == 'past':
                search = search.filter(Exhibition.end_date < today)
    
    # Return a list so callers/templates won't receive a Query object
    return search.order_by(Exhibition.start_date.desc()).all()