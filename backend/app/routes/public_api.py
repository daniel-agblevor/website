import re
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, limiter
from app.models import (
    Lead, PortfolioProject, CaseStudy, Testimonial,
    BlogPost, SlideshowImage, SiteProfile, FeatureFlag
)
from app.services.email_service import send_new_lead_notification

public_bp = Blueprint('public_api', __name__, url_prefix='/api')

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@public_bp.route('/contact', methods=['POST'])
@limiter.limit("5 per minute")
def submit_contact_form():
    """Public contact form submission endpoint with validation and rate limiting"""
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    service_interest = data.get('service_interest', '').strip()
    message = data.get('message', '').strip()

    # Input validation
    errors = []
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters long.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("Please provide a valid email address.")
    if not message or len(message) < 10:
        errors.append("Message must be at least 10 characters long.")

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    try:
        new_lead = Lead(
            name=name,
            email=email,
            phone=phone if phone else None,
            service_interest=service_interest if service_interest else "General Consulting",
            message=message,
            status='new'
        )
        db.session.add(new_lead)
        db.session.commit()

        # Send email notification asynchronously or in background
        send_new_lead_notification(new_lead.to_dict())

        return jsonify({
            "message": "Thank you! Your inquiry has been submitted successfully.",
            "lead_id": new_lead.id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving lead: {e}")
        return jsonify({"error": "Failed to submit contact form. Please try again later."}), 500


@public_bp.route('/features', methods=['GET'])
def get_features():
    """Public endpoint to fetch active feature toggles"""
    default_flags = {
        "services": True,
        "portfolio": True,
        "case_studies": True,
        "testimonials": True,
        "blog": True
    }
    try:
        flags = FeatureFlag.query.all()
        flag_dict = {f.feature_name: f.is_enabled for f in flags}
        # Merge with defaults
        for k, v in default_flags.items():
            if k not in flag_dict:
                flag_dict[k] = v
        return jsonify(flag_dict), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching feature flags: {e}")
        return jsonify(default_flags), 200


@public_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Public endpoint for portfolio projects (respects feature flag)"""
    flag = FeatureFlag.query.filter_by(feature_name='portfolio').first()
    if flag and not flag.is_enabled:
        return jsonify([]), 200

    projects = PortfolioProject.query.order_by(PortfolioProject.sort_order.asc(), PortfolioProject.id.asc()).all()
    return jsonify([p.to_dict() for p in projects]), 200


@public_bp.route('/case-studies', methods=['GET'])
def get_case_studies():
    """Public endpoint for case studies (respects feature flag)"""
    flag = FeatureFlag.query.filter_by(feature_name='case_studies').first()
    if flag and not flag.is_enabled:
        return jsonify([]), 200

    studies = CaseStudy.query.order_by(CaseStudy.sort_order.asc(), CaseStudy.id.asc()).all()
    return jsonify([s.to_dict() for s in studies]), 200


@public_bp.route('/testimonials', methods=['GET'])
def get_testimonials():
    """Public endpoint for client testimonials (respects feature flag)"""
    flag = FeatureFlag.query.filter_by(feature_name='testimonials').first()
    if flag and not flag.is_enabled:
        return jsonify([]), 200

    testimonials = Testimonial.query.order_by(Testimonial.sort_order.asc(), Testimonial.id.asc()).all()
    return jsonify([t.to_dict() for t in testimonials]), 200


@public_bp.route('/blog', methods=['GET'])
def get_blog_posts():
    """Public endpoint for blog post excerpts (respects feature flag)"""
    flag = FeatureFlag.query.filter_by(feature_name='blog').first()
    if flag and not flag.is_enabled:
        return jsonify([]), 200

    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc()).all()
    return jsonify([p.to_dict() for p in posts]), 200


@public_bp.route('/slideshow', methods=['GET'])
def get_slideshow():
    """Public endpoint for homepage photo carousel"""
    slides = SlideshowImage.query.order_by(SlideshowImage.sort_order.asc(), SlideshowImage.id.asc()).all()
    return jsonify([s.to_dict() for s in slides]), 200


@public_bp.route('/profile', methods=['GET'])
def get_profile():
    """Public endpoint for consultant profile photo & intro video URL"""
    profile = SiteProfile.query.first()
    if not profile:
        profile = SiteProfile(
            profile_photo_url="",
            intro_video_url="",
            bio_headline="HR Systems & Automation Freelance Consultant",
            bio_summary="Empowering organizations in Accra and beyond with seamless payroll, attendance, Power BI dashboards, and custom VBA tools."
        )
        db.session.add(profile)
        db.session.commit()

    return jsonify(profile.to_dict()), 200
