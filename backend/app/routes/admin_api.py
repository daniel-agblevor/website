from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.auth import generate_admin_token, verify_supabase_user, admin_required
from app.models import (
    Lead, PortfolioProject, CaseStudy, Testimonial,
    BlogPost, SlideshowImage, SiteProfile, FeatureFlag
)

admin_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')


@admin_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint using Supabase Auth or configured credentials"""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    auth_result = verify_supabase_user(email, password)
    if not auth_result.get("success"):
        return jsonify({"error": auth_result.get("error", "Authentication failed")}), 401

    token = generate_admin_token(auth_result.get("user_id", "admin"), email)

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "email": email
    }), 200


# --- LEADS MANAGEMENT ---

@admin_bp.route('/leads', methods=['GET'])
@admin_required
def get_leads():
    """Fetch paginated/filtered list of leads for admin dashboard"""
    status = request.args.get('status', '').strip().lower()
    query = Lead.query

    if status in ['new', 'contacted', 'closed']:
        query = query.filter_by(status=status)

    leads = query.order_by(Lead.created_at.desc()).all()
    return jsonify([l.to_dict() for l in leads]), 200


@admin_bp.route('/leads/<int:lead_id>', methods=['PATCH'])
@admin_required
def update_lead_status(lead_id):
    """Update lead status ('new', 'contacted', 'closed')"""
    lead = Lead.query.get_or_404(lead_id)
    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if new_status not in ['new', 'contacted', 'closed']:
        return jsonify({"error": "Invalid status value. Must be 'new', 'contacted', or 'closed'."}), 400

    lead.status = new_status
    db.session.commit()

    return jsonify({"message": "Lead status updated successfully", "lead": lead.to_dict()}), 200


# --- FEATURE FLAGS ---

@admin_bp.route('/features/<feature_name>', methods=['PATCH'])
@admin_required
def toggle_feature_flag(feature_name):
    """Toggle a public feature section on/off"""
    data = request.get_json() or {}
    is_enabled = data.get('is_enabled')

    if is_enabled is not bool and not isinstance(is_enabled, bool):
        return jsonify({"error": "is_enabled must be a boolean"}), 400

    flag = FeatureFlag.query.filter_by(feature_name=feature_name).first()
    if not flag:
        flag = FeatureFlag(feature_name=feature_name, is_enabled=is_enabled)
        db.session.add(flag)
    else:
        flag.is_enabled = is_enabled

    db.session.commit()
    return jsonify({"message": f"Feature '{feature_name}' updated", "flag": flag.to_dict()}), 200


# --- PORTFOLIO CRUD ---

@admin_bp.route('/portfolio', methods=['POST'])
@admin_required
def create_portfolio_project():
    data = request.get_json() or {}
    tech_pills = data.get('tech_pills', '')
    if isinstance(tech_pills, list):
        tech_pills = ", ".join(tech_pills)

    project = PortfolioProject(
        title=data.get('title', '').strip(),
        description=data.get('description', '').strip(),
        external_link=data.get('external_link', '').strip(),
        tech_pills=tech_pills,
        youtube_video_url=data.get('youtube_video_url', '').strip(),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@admin_bp.route('/portfolio/<int:project_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_portfolio_project(project_id):
    project = PortfolioProject.query.get_or_404(project_id)
    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200

    data = request.get_json() or {}
    tech_pills = data.get('tech_pills', project.tech_pills)
    if isinstance(tech_pills, list):
        tech_pills = ", ".join(tech_pills)

    project.title = data.get('title', project.title).strip()
    project.description = data.get('description', project.description).strip()
    project.external_link = data.get('external_link', project.external_link).strip()
    project.tech_pills = tech_pills
    project.youtube_video_url = data.get('youtube_video_url', project.youtube_video_url).strip()
    project.sort_order = data.get('sort_order', project.sort_order)

    db.session.commit()
    return jsonify(project.to_dict()), 200


# --- CASE STUDIES CRUD ---

@admin_bp.route('/case-studies', methods=['POST'])
@admin_required
def create_case_study():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    slug = data.get('slug', '').strip() or title.lower().replace(' ', '-')
    study = CaseStudy(
        title=title,
        slug=slug,
        summary=data.get('summary', '').strip(),
        content=data.get('content', '').strip(),
        image_url=data.get('image_url', '').strip(),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(study)
    db.session.commit()
    return jsonify(study.to_dict()), 201


@admin_bp.route('/case-studies/<int:study_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_case_study(study_id):
    study = CaseStudy.query.get_or_404(study_id)
    if request.method == 'DELETE':
        db.session.delete(study)
        db.session.commit()
        return jsonify({"message": "Case study deleted successfully"}), 200

    data = request.get_json() or {}
    study.title = data.get('title', study.title).strip()
    study.slug = data.get('slug', study.slug).strip()
    study.summary = data.get('summary', study.summary).strip()
    study.content = data.get('content', study.content).strip()
    study.image_url = data.get('image_url', study.image_url).strip()
    study.sort_order = data.get('sort_order', study.sort_order)

    db.session.commit()
    return jsonify(study.to_dict()), 200


# --- TESTIMONIALS CRUD ---

@admin_bp.route('/testimonials', methods=['POST'])
@admin_required
def create_testimonial():
    data = request.get_json() or {}
    testimonial = Testimonial(
        client_name=data.get('client_name', '').strip(),
        company=data.get('company', '').strip(),
        role=data.get('role', '').strip(),
        quote=data.get('quote', '').strip(),
        rating=data.get('rating', 5),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(testimonial)
    db.session.commit()
    return jsonify(testimonial.to_dict()), 201


@admin_bp.route('/testimonials/<int:item_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_testimonial(item_id):
    testimonial = Testimonial.query.get_or_404(item_id)
    if request.method == 'DELETE':
        db.session.delete(testimonial)
        db.session.commit()
        return jsonify({"message": "Testimonial deleted successfully"}), 200

    data = request.get_json() or {}
    testimonial.client_name = data.get('client_name', testimonial.client_name).strip()
    testimonial.company = data.get('company', testimonial.company).strip()
    testimonial.role = data.get('role', testimonial.role).strip()
    testimonial.quote = data.get('quote', testimonial.quote).strip()
    testimonial.rating = data.get('rating', testimonial.rating)
    testimonial.sort_order = data.get('sort_order', testimonial.sort_order)

    db.session.commit()
    return jsonify(testimonial.to_dict()), 200


# --- BLOG CRUD ---

@admin_bp.route('/blog', methods=['POST'])
@admin_required
def create_blog_post():
    data = request.get_json() or {}
    post = BlogPost(
        title=data.get('title', '').strip(),
        excerpt=data.get('excerpt', '').strip(),
        full_content=data.get('full_content', '').strip(),
        linkedin_url=data.get('linkedin_url', '').strip(),
        is_published=data.get('is_published', True)
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201


@admin_bp.route('/blog/<int:post_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Blog post deleted successfully"}), 200

    data = request.get_json() or {}
    post.title = data.get('title', post.title).strip()
    post.excerpt = data.get('excerpt', post.excerpt).strip()
    post.full_content = data.get('full_content', post.full_content).strip()
    post.linkedin_url = data.get('linkedin_url', post.linkedin_url).strip()
    post.is_published = data.get('is_published', post.is_published)

    db.session.commit()
    return jsonify(post.to_dict()), 200


# --- SLIDESHOW CRUD ---

@admin_bp.route('/slideshow', methods=['POST'])
@admin_required
def create_slideshow_image():
    data = request.get_json() or {}
    slide = SlideshowImage(
        image_url=data.get('image_url', '').strip(),
        caption=data.get('caption', '').strip(),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(slide)
    db.session.commit()
    return jsonify(slide.to_dict()), 201


@admin_bp.route('/slideshow/<int:slide_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_slideshow_image(slide_id):
    slide = SlideshowImage.query.get_or_404(slide_id)
    if request.method == 'DELETE':
        db.session.delete(slide)
        db.session.commit()
        return jsonify({"message": "Slideshow image deleted successfully"}), 200

    data = request.get_json() or {}
    slide.image_url = data.get('image_url', slide.image_url).strip()
    slide.caption = data.get('caption', slide.caption).strip()
    slide.sort_order = data.get('sort_order', slide.sort_order)

    db.session.commit()
    return jsonify(slide.to_dict()), 200


# --- PROFILE UPDATE ---

@admin_bp.route('/profile', methods=['PUT'])
@admin_required
def update_profile():
    profile = SiteProfile.query.first()
    if not profile:
        profile = SiteProfile()
        db.session.add(profile)

    data = request.get_json() or {}
    profile.profile_photo_url = data.get('profile_photo_url', profile.profile_photo_url).strip()
    profile.intro_video_url = data.get('intro_video_url', profile.intro_video_url).strip()
    profile.bio_headline = data.get('bio_headline', profile.bio_headline).strip()
    profile.bio_summary = data.get('bio_summary', profile.bio_summary).strip()

    db.session.commit()
    return jsonify(profile.to_dict()), 200
