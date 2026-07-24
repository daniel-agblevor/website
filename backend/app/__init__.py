import os
from flask import Flask, send_from_directory
from app.config import config_by_name
from app.extensions import db, cors, limiter
from app.routes.public_api import public_bp
from app.routes.admin_api import admin_bp

def create_app(config_name=None):
    """Application Factory Pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Resolve the docs/ frontend folder relative to this file's location.
    # File lives at: backend/app/__init__.py
    # docs/ lives at: ../../docs  (two levels up from app/, then into docs/)
    docs_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
    )

    app = Flask(__name__, static_folder=docs_dir, static_url_path='')

    # Load configuration
    config_cls = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_cls)

    # Initialize extensions
    db.init_app(app)

    # Configure CORS strictly to frontend origin
    allowed_origins = [app.config.get("FRONTEND_URL", "*")]
    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}})

    limiter.init_app(app)

    # Register API blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Serve static frontend for local dev / testing
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    # Serve private admin panel at obscure route
    admin_slug = app.config.get("ADMIN_ROUTE_PATH", "/admin-portal").strip('/')

    @app.route(f'/{admin_slug}')
    @app.route(f'/{admin_slug}/')
    def serve_admin():
        admin_dir = os.path.join(app.static_folder, 'admin')
        return send_from_directory(admin_dir, 'index.html')

    # Create tables on startup (catches errors gracefully)
    with app.app_context():
        try:
            db.create_all()
            seed_initial_data()
        except Exception as e:
            app.logger.warning(f"Could not auto-create database tables on startup: {e}")

    return app


def seed_initial_data():
    """Seeds initial sample content and feature flags if database is empty"""
    from app.models import FeatureFlag, SiteProfile, PortfolioProject, SlideshowImage, BlogPost, Testimonial

    # Seed Feature Flags
    if FeatureFlag.query.count() == 0:
        flags = [
            FeatureFlag(feature_name='services', is_enabled=True),
            FeatureFlag(feature_name='portfolio', is_enabled=True),
            FeatureFlag(feature_name='case_studies', is_enabled=True),
            FeatureFlag(feature_name='testimonials', is_enabled=True),
            FeatureFlag(feature_name='blog', is_enabled=True)
        ]
        db.session.bulk_save_objects(flags)

    # Seed Profile
    if SiteProfile.query.count() == 0:
        profile = SiteProfile(
            profile_photo_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=600&q=80",
            intro_video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            bio_headline="HR Systems & Automation Specialist | ICAG & AWS Certified",
            bio_summary="Based in Accra, Ghana. Transforming complex HR operations into automated, error-free workflows. Specialized in custom payroll systems, biometrics attendance integration, Power BI executive dashboards, and VBA tooling."
        )
        db.session.add(profile)

    # Seed Sample Portfolio Projects
    if PortfolioProject.query.count() == 0:
        projects = [
            PortfolioProject(
                title="Automated Payroll & Tax Reconciliation System",
                description="Custom end-to-end payroll engine calculated with Ghana GRA tax brackets, SSNIT deductions, tier-2 pension schedules, and instant payslip PDF generation.",
                external_link="https://github.com",
                tech_pills="Python, Excel VBA, PostgreSQL, Power BI",
                youtube_video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                sort_order=1
            ),
            PortfolioProject(
                title="Biometric Attendance & Leave Management Pipeline",
                description="Real-time data pipeline synchronizing ZKeco attendance clocks with leave request workflows, producing automated monthly attendance audits.",
                external_link="https://github.com",
                tech_pills="Flask, REST API, Supabase, JavaScript",
                youtube_video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                sort_order=2
            ),
            PortfolioProject(
                title="Executive HR Analytics & Workforce Dashboard",
                description="Interactive Power BI reporting suite tracking turnover rate, headcount trends, overtime costs, and KPI benchmarks across regional branches.",
                external_link="https://github.com",
                tech_pills="Power BI, DAX, SQL, Data Pipeline",
                youtube_video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                sort_order=3
            )
        ]
        db.session.bulk_save_objects(projects)

    # Seed Sample Slideshow Images
    if SlideshowImage.query.count() == 0:
        slides = [
            SlideshowImage(image_url="https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1000&q=80", caption="Conducting HR Automation Masterclass in Accra", sort_order=1),
            SlideshowImage(image_url="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1000&q=80", caption="Collaborating on Enterprise HR Transformation Project", sort_order=2),
            SlideshowImage(image_url="https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1000&q=80", caption="Presenting Power BI HR Executive Insights", sort_order=3),
        ]
        db.session.bulk_save_objects(slides)

    # Seed Sample Blog Posts
    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(
                title="Why Ghana Enterprises Are Automating Payroll Reconciliation in 2026",
                excerpt="Manual tax computation and SSNIT reconciliation cost HR teams hundreds of hours every quarter. Here is how modern automation solves it.",
                full_content="Manual payroll computation remains one of the largest operational bottlenecks for growing organizations in West Africa. By integrating automated GRA tax table calculations with digital payslip distribution, finance and HR teams eliminate human error, ensure statutory compliance, and reduce processing times from days to minutes.",
                linkedin_url="https://www.linkedin.com"
            ),
            BlogPost(
                title="Building a Data-Driven HR Department with Power BI & Python",
                excerpt="Transform raw attendance and performance logs into actionable executive dashboards that highlight retention trends.",
                full_content="Data-driven HR is no longer optional. By combining Python scripts for ETL data extraction with Power BI interactive dashboards, leadership gains instant visibility into attendance anomalies, overtime expenses, and department efficiency metrics.",
                linkedin_url="https://www.linkedin.com"
            )
        ]
        db.session.bulk_save_objects(posts)

    # Seed Sample Testimonials
    if Testimonial.query.count() == 0:
        reviews = [
            Testimonial(
                client_name="Kwame Mensah",
                company="Accra Logistics Ltd",
                role="Head of Human Resources",
                quote="The automated payroll and attendance solution transformed our monthly operations. What used to take our team 4 full days is now completed in 20 minutes with zero tax calculation discrepancies.",
                rating=5,
                sort_order=1
            ),
            Testimonial(
                client_name="Abena Osei",
                company="WestCoast Financial Services",
                role="Operations Director",
                quote="Exceptional technical expertise in both accounting principles and Python automation. The Power BI HR dashboard gives our executive board real-time visibility into workforce metrics.",
                rating=5,
                sort_order=2
            )
        ]
        db.session.bulk_save_objects(reviews)

    db.session.commit()
