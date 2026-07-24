from datetime import datetime
from app.extensions import db

class Lead(db.Model):
    """Contact form submissions and leads"""
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    service_interest = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new', nullable=False) # 'new', 'contacted', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "service_interest": self.service_interest,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PortfolioProject(db.Model):
    """Portfolio Showcase Items"""
    __tablename__ = 'portfolio_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    external_link = db.Column(db.String(300), nullable=True)
    tech_pills = db.Column(db.String(300), nullable=True) # Comma-separated or JSON string, e.g. "Python, Power BI, VBA"
    youtube_video_url = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        pills = [p.strip() for p in self.tech_pills.split(',')] if self.tech_pills else []
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "external_link": self.external_link,
            "tech_pills": pills,
            "youtube_video_url": self.youtube_video_url,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CaseStudy(db.Model):
    """In-Depth Case Studies"""
    __tablename__ = 'case_studies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "content": self.content,
            "image_url": self.image_url,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Testimonial(db.Model):
    """Client Reviews / Testimonials"""
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(120), nullable=True)
    quote = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "company": self.company,
            "role": self.role,
            "quote": self.quote,
            "rating": self.rating,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class BlogPost(db.Model):
    """Blog Articles (Excerpts on site, full content in modal, LinkedIn links)"""
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    full_content = db.Column(db.Text, nullable=False)
    linkedin_url = db.Column(db.String(300), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "excerpt": self.excerpt,
            "full_content": self.full_content,
            "linkedin_url": self.linkedin_url,
            "published_at": self.published_at.strftime('%B %d, %Y') if self.published_at else None,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SlideshowImage(db.Model):
    """Homepage Photo Carousel (up to 15 images)"""
    __tablename__ = 'slideshow_images'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "caption": self.caption,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SiteProfile(db.Model):
    """Singleton site profile record (Photo & YouTube Intro URL)"""
    __tablename__ = 'site_profile'

    id = db.Column(db.Integer, primary_key=True)
    profile_photo_url = db.Column(db.String(500), nullable=True)
    intro_video_url = db.Column(db.String(500), nullable=True)
    bio_headline = db.Column(db.String(255), nullable=True)
    bio_summary = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_photo_url": self.profile_photo_url,
            "intro_video_url": self.intro_video_url,
            "bio_headline": self.bio_headline,
            "bio_summary": self.bio_summary,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class FeatureFlag(db.Model):
    """Dynamic section feature toggles controlled via admin panel"""
    __tablename__ = 'feature_flags'

    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(50), nullable=False, unique=True) # e.g. 'services', 'portfolio', 'case_studies', 'testimonials', 'blog'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "feature_name": self.feature_name,
            "is_enabled": self.is_enabled
        }
