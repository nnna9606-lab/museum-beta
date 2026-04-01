
from flask import Flask, render_template, request, redirect, url_for, flash
from typing import Optional
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from image_utils import save_image, delete_image
from werkzeug.utils import secure_filename
from translations import get_translation, translations as all_translations
import os
import smtplib
import ssl
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///museum.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-length
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Փոխեք այս բանալին
# Mail settings (configure in production with environment variables)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587) or 587)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@example.com')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Խնդրում ենք մուտք գործել այս էջը դիտելու համար:'

# --- Admin: Delete all chat messages with a user ---
@app.route('/admin/user/<int:user_id>/delete_chat', methods=['POST'], endpoint='admin_delete_user_chat')
@login_required
def admin_delete_user_chat(user_id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('admin_users'))
    user = User.query.get_or_404(user_id)
    deleted = MuseumQuestion.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash(f'Օգտատիրոջ (ID={user_id}) բոլոր նամակները ջնջվեցին ({deleted} հատ)։')
    return redirect(url_for('admin_users'))



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' կամ 'user'
    _is_active = db.Column('is_active', db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    profile_image = db.Column(db.String(200))

    # Add favorites relationships
    favorites_artifacts = db.relationship(
        'Artifact',
        secondary='user_favorite_artifacts',
        backref='favorited_by_users'
    )
    favorites_exhibitions = db.relationship(
        'Exhibition',
        secondary='user_favorite_exhibitions',
        backref='favorited_by_users'
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_active(self) -> bool:
        # Flask-Login expects this to always return True for active accounts
        return bool(self._is_active)

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value

    @property
    def is_account_active(self) -> bool:
        # Use this property in your own code to check if the account is really active
        return bool(self._is_active)
        
    def get_dashboard_url(self) -> str:
        return url_for('admin_dashboard' if self.is_admin else 'user_dashboard')

    def get_profile_image_url(self) -> str:
        if self.profile_image:
            return url_for('static', filename=f'uploads/{self.profile_image}')
        return url_for('static', filename='default-profile.png')

    @property
    def favorites_artifact_ids(self) -> list[int]:
        if hasattr(self, 'favorites_artifacts'):
            return [a.id for a in self.favorites_artifacts]
        return []

@login_manager.user_loader
def load_user(user_id: int) -> 'Optional[User]':
    return User.query.get(int(user_id))

class Exhibition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Only Armenian fields remain
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    artifacts = db.relationship('Artifact', secondary='exhibition_artifacts', backref='exhibitions')
    images = db.relationship('ExhibitionImage', backref='exhibition', cascade='all, delete-orphan')
    

    def get_title(self, lang=None):
        """Get exhibition title (supports future multilingual)"""
        return self.title

    def get_description(self, lang=None):
        """Get exhibition description (supports future multilingual)"""
        return self.description



# Favorites association tables
user_favorite_artifacts = db.Table('user_favorite_artifacts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('artifact_id', db.Integer, db.ForeignKey('artifact.id'), primary_key=True)
)

user_favorite_exhibitions = db.Table('user_favorite_exhibitions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('exhibition_id', db.Integer, db.ForeignKey('exhibition.id'), primary_key=True)
)




class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    obj_type = db.Column(db.String(50))
    obj_id = db.Column(db.Integer)
    meta = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def log_action(user: 'User', action: str, obj_type: str = None, obj_id: int = None, meta: str = None) -> None:
    try:
        audit = Audit(
            user_id=(getattr(user, 'id', None) if user else None),
            action=action,
            obj_type=obj_type,
            obj_id=obj_id,
            meta=meta
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()


# --- Email and token helpers -------------------------------------------------
def _get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_reset_token(email: str) -> str:
    s = _get_serializer()
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token: str, max_age: int = 3600):
    try:
        s = _get_serializer()
        email = s.loads(token, salt='password-reset-salt', max_age=max_age)
        return email
    except Exception:
        return None

def send_email(to_email: str, subject: str, body: str):
    server = app.config.get('MAIL_SERVER')
    if not server:
        # Mail not configured — skip sending in development but log
        app.logger.warning('Mail server not configured; skipping send to %s', to_email)
        return False

    port = app.config.get('MAIL_PORT', 587)
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    use_tls = app.config.get('MAIL_USE_TLS', True)
    use_ssl = app.config.get('MAIL_USE_SSL', False)
    sender = app.config.get('MAIL_DEFAULT_SENDER')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(body)

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(server, port, context=context) as smtp:
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(server, port) as smtp:
                if use_tls:
                    smtp.starttls(context=ssl.create_default_context())
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(msg)
        app.logger.info('Sent email to %s', to_email)
        return True
    except Exception as e:
        app.logger.exception('Failed to send email: %s', e)
        return False

def send_password_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = 'Թվայնացված Թանգարան - Գաղտնաբառի վերականգնում'
    body = f"Ողջույն {user.username},\n\nԵթե ցանկանում եք վերականգնել ձեր գաղտնաբառը, սեղմեք ներքա՛յն հղումը կամ պատճենեք այն բրաուզերի մեջ:\n\n{reset_url}\n\nԵթե դուք չեք խնդրատել վերականգնում, կարող եք անտեսել այս նամակը.\n\nՇնորհակալություն,\nԹվայնացված Թանգարան"
    return send_email(user.email, subject, body)


class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    name_ru = db.Column(db.String(100), nullable=True)  # Russian name
    name_en = db.Column(db.String(100), nullable=True)  # English name
    description_ru = db.Column(db.Text, nullable=True)  # Russian description
    description_en = db.Column(db.Text, nullable=True)  # English description
    year = db.Column(db.Integer)
    image_url = db.Column(db.String(200))
    thumbnail_url = db.Column(db.String(200))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Պահել որպես JSON
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('ArtifactImage', backref='artifact', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_name(self, lang='hy'):
        """Get artifact name in specified language"""
        if lang == 'ru':
            return self.name_ru or self.name
        elif lang == 'en':
            return self.name_en or self.name
        return self.name
    
    def get_description(self, lang='hy'):
        """Get artifact description in specified language"""
        if lang == 'ru':
            return self.description_ru or self.description
        elif lang == 'en':
            return self.description_en or self.description
        return self.description
    
    def get_image_url(self):
        """Վերադարձնել նկարի ամբողջական URL-ը"""
        if self.image_url:
            # If image_url is an external URL (http/https) or absolute path, return as-is
            if self.image_url.startswith('http') or self.image_url.startswith('/'):
                return self.image_url
            return url_for('static', filename=f'uploads/{self.image_url}')
        return url_for('static', filename='default-artifact.jpg')
    
    def get_thumbnail_url(self):
        """Վերադարձնել փոքր նկարի ամբողջական URL-ը"""
        if self.thumbnail_url:
            if self.thumbnail_url.startswith('http') or self.thumbnail_url.startswith('/'):
                return self.thumbnail_url
            return url_for('static', filename=f'uploads/{self.thumbnail_url}')
        return url_for('static', filename='default-thumbnail.jpg')
    
    def get_all_images(self):
        """Վերադարձնել բոլոր նկարները"""
        return self.images.all()


class ArtifactImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifact.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    thumbnail_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_image_url(self):
        """Վերադարձնել նկարի ամբողջական URL-ը"""
        if self.image_url:
            if self.image_url.startswith('http') or self.image_url.startswith('/'):
                return self.image_url
            return url_for('static', filename=f'uploads/{self.image_url}')
        return url_for('static', filename='default-artifact.jpg')
    
    def get_thumbnail_url(self):
        """Վերադարձնել փոքր նկարի ամբողջական URL-ը"""
        if self.thumbnail_url:
            return url_for('static', filename=f'uploads/{self.thumbnail_url}')
        return self.get_image_url()


class ExhibitionImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, db.ForeignKey('exhibition.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    caption = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_image_url(self):
        # If URL is external (http), return as-is; otherwise treat as uploaded
        if self.image_url and (self.image_url.startswith('http') or self.image_url.startswith('/')):
            return self.image_url
        if self.image_url:
            return url_for('static', filename=f'uploads/{self.image_url}')
        return url_for('static', filename='default-exhibit.jpg')

# Կապող աղյուսակ ցուցադրությունների և նմուշների միջև
exhibition_artifacts = db.Table('exhibition_artifacts',
    db.Column('exhibition_id', db.Integer, db.ForeignKey('exhibition.id'), primary_key=True),
    db.Column('artifact_id', db.Integer, db.ForeignKey('artifact.id'), primary_key=True)
)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate input
        if not username or not email or not password:
            flash('Խնդրում ենք լրացնել բոլոր դաշտերը')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Գաղտնաբառը պետք է լինի նվազ 6 նիշ')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Այս օգտանունն արդեն զբաղված է')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Այս էլ. հասցեն արդեն օգտագործվում է')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # Log registration
        log_action(user, 'register', obj_type='user', obj_id=user.id)

        # Send welcome / password-recovery email (if mail configured)
        try:
            sent = send_password_reset_email(user)
            if sent:
                flash('Գրանցումը հաջողությամբ ավարտվեց. մենք ուղարկեցինք նամակ՝ ձեր էլ. փոստին')
            else:
                flash('Գրանցումը հաջողությամբ ավարտվեց. (էլ. նամակ չի ուղարկվել՝ կոնֆիգ չի հայտնաբերվել)')
        except Exception:
            flash('Գրանցումը հաջողությամբ ավարտվեց')

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(current_user.get_dashboard_url())
    
    if request.method == 'POST':
        # Handle missing form fields gracefully
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Խնդրում ենք մուտքագրել օգտանուն և գաղտնաբառ')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Ձեր հաշիվը ապաակտիվացված է')
                return redirect(url_for('login'))
            
            remember_me = request.form.get('remember') is not None
            login_user(user, remember=remember_me)
            return redirect(user.get_dashboard_url())
        else:
            flash('Սխալ օգտանուն կամ գաղտնաբառ')
            
    return render_template('login.html')


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Խնդրում ենք մուտքագրել էլ. հասցե')
            return redirect(url_for('reset_password_request'))

        user = User.query.filter_by(email=email).first()
        # Always show the same message to avoid leaking which emails are registered
        if user:
            try:
                send_password_reset_email(user)
            except Exception:
                app.logger.exception('Failed to send reset email')

        flash('Եթե այս էլ. հասցեն գտնվել է մեր համակարգում՝ դուք կստանաք նամակ հետվերականգնման համար։')
        return redirect(url_for('login'))

    return render_template('reset_password_request.html')


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Գործողության ժամանակը ավարտվել է կամ տոմսը անվավեր է')
        return redirect(url_for('reset_password_request'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Օգտատերը չի գտնվել')
        return redirect(url_for('reset_password_request'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        if not password:
            flash('Խնդրում ենք մուտքագրել նոր գաղտնաբառ')
            return redirect(url_for('reset_password', token=token))
        user.set_password(password)
        db.session.commit()
        log_action(user, 'reset_password', obj_type='user', obj_id=user.id)
        flash('Ձեր գաղտնաբառը հաջողությամբ թարմացվեց՝ կարող եք մուտք գործել')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Այս էջը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
        
    users = User.query.all()
    artifacts = Artifact.query.all()
    exhibitions = Exhibition.query.all()
    
    return render_template('admin/dashboard.html', 
                         users=users,
                         artifacts=artifacts,
                         exhibitions=exhibitions)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user_artifacts = Artifact.query.filter_by(user_id=current_user.id).all()
    exhibitions = Exhibition.query.all()
    
    return render_template('user/dashboard.html',
                         artifacts=user_artifacts,
                         exhibitions=exhibitions,
                         today=datetime.now().date())


@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User profile settings: update username, email and password."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        current_pwd = request.form.get('current_password', '')

        # Validate uniqueness for username
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Այս օգտանունն արդեն օգտագործվում է')
                return redirect(url_for('user_settings'))
            current_user.username = username

        # Validate uniqueness for email
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Այս էլ. հասցեն արդեն օգտագործվում է')
                return redirect(url_for('user_settings'))
            current_user.email = email

        # If user requested password change, require current password verification
        if password:
            if not current_pwd:
                flash('Խնդրում ենք մուտքագրել ձեր ընթացիկ գաղտնաբառը՝ փոփոխությունը հաստատելու համար')
                return redirect(url_for('user_settings'))
            if not current_user.check_password(current_pwd):
                flash('Ընթացիկ գաղտնաբառը սխալ է')
                return redirect(url_for('user_settings'))
            current_user.set_password(password)

        # If user provided a profile image, save it
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                res = save_image(file)
                if res:
                    # delete previous image if exists
                    try:
                        delete_image(current_user.profile_image)
                    except Exception:
                        pass
                    current_user.profile_image = res['filename']
                else:
                    flash('Ընտրված ֆայլը անթույլատրելի է կամ մեծ չափի է')
                    return redirect(url_for('user_settings'))

        try:
            db.session.commit()
            log_action(current_user, 'update_profile', obj_type='user', obj_id=current_user.id)
            flash('Ձեր կարգավորումները հաջողությամբ թարմացվել են')
        except Exception:
            db.session.rollback()
            flash('Սխալ պահպանման ընթացքում՝ փորձեք կրկին')
        return redirect(url_for('user_settings'))

    return render_template('user/settings.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Այս էջը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/<int:id>/toggle')
@login_required
def toggle_user(id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
        
    user = User.query.get_or_404(id)
    if user.id != current_user.id:  # Ադմինը չի կարող ապաակտիվացնել իր հաշիվը
        user.is_active = not user.is_active
        db.session.commit()
        # Log the toggle action
        log_action(current_user, 'toggle_user', obj_type='user', obj_id=user.id, meta=f'is_active={user.is_active}')
    return redirect(url_for('admin_users'))

# Language handling
@app.before_request
def before_request():
    # Get language from cookie, request args, or default to Armenian
    lang = request.args.get('lang') or request.cookies.get('language') or 'hy'
    if lang not in all_translations:
        lang = 'hy'
    
    from flask import g
    g.language = lang
    g.get_text = lambda key: get_translation(key, lang)
    g.all_languages = list(all_translations.keys())

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang not in all_translations:
        lang = 'hy'
    
    response = redirect(request.referrer or url_for('index'))
    response.set_cookie('language', lang, max_age=60*60*24*365)  # 1 year
    return response

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    # Show recent artifacts and featured exhibitions on the homepage
    artifacts = Artifact.query.order_by(Artifact.id.desc()).limit(12).all()
    exhibitions = Exhibition.query.order_by(Exhibition.start_date.desc()).limit(3).all()
    # Pass 'today' so templates can evaluate exhibition status without UndefinedError
    return render_template('index.html', artifacts=artifacts, exhibitions=exhibitions, today=datetime.now().date())

@app.route('/artifacts')
def artifacts():
    """Ցուցադրել նմուշները՝ հնարավոր որոնման ֆիլտրերով։"""
    query = Artifact.query

    # Ստուգել որոնման պարամետրերը
    name = request.args.get('name', '').strip()
    if name:
        query = query.filter(Artifact.name.ilike(f'%{name}%'))

    year = request.args.get('year')
    if year and year.isdigit():
        query = query.filter(Artifact.year == int(year))

    category = request.args.get('category')
    if category:
        query = query.filter(Artifact.category == category)

    # Դասավորել ըստ ստեղծման ամսաթվի (նորից հին)
    artifacts_list = query.order_by(Artifact.created_at.desc()).all()

    return render_template('artifacts.html', artifacts=artifacts_list)

@app.route('/artifact/<int:id>')
def artifact_detail(id):
    # Artifact details are viewable by anonymous users as well
    artifact = Artifact.query.get_or_404(id)
    return render_template('detail.html', artifact=artifact)


@app.route('/artifact/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_artifact(id):
    # Only admins can edit artifacts
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('artifact_detail', id=id))

    artifact = Artifact.query.get_or_404(id)
    if request.method == 'POST':
        artifact.name = request.form['name']
        artifact.description = request.form['description']
        # Year may be empty or non-numeric
        year_val = request.form.get('year')
        artifact.year = int(year_val) if year_val and year_val.isdigit() else None
        artifact.category = request.form.get('category')
        artifact.tags = request.form.get('tags')

        # Handle uploaded image file (preferred) or external URL
        file = request.files.get('image_file')
        if file and getattr(file, 'filename', ''):
            res = save_image(file)
            if res:
                # delete previous image files
                try:
                    delete_image(artifact.image_url)
                except Exception:
                    pass
                artifact.image_url = res['filename']
                # save thumbnail basename for URL helper
                artifact.thumbnail_url = os.path.basename(res.get('thumbnail_path', ''))
            else:
                flash('Ընտրված ֆայլը անթույլատրելի է կամ մեծ չափի է')
                return redirect(url_for('edit_artifact', id=id))
        else:
            # allow external URL or manual filename
            artifact.image_url = request.form.get('image_url')

        # Handle additional uploaded images
        files = request.files.getlist('additional_images')
        for file in files:
            if file and getattr(file, 'filename', ''):
                res = save_image(file)
                if res:
                    artifact_image = ArtifactImage(
                        artifact_id=artifact.id,
                        image_url=res['filename'],
                        thumbnail_url=os.path.basename(res.get('thumbnail_path', ''))
                    )
                    db.session.add(artifact_image)

        db.session.commit()
        flash('Նմուշը հաջողությամբ թարմացվեց')
        # Log edit
        log_action(current_user, 'edit_artifact', obj_type='artifact', obj_id=artifact.id)
        return redirect(url_for('artifact_detail', id=artifact.id))

    return render_template('edit_artifact.html', artifact=artifact)


@app.route('/artifact/<int:id>/delete', methods=['POST'])
@login_required
def delete_artifact(id):
    # Only admins can delete artifacts
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('artifact_detail', id=id))

    artifact = Artifact.query.get_or_404(id)
    db.session.delete(artifact)
    db.session.commit()
    # Log delete (note: obj_id stored even after delete)
    log_action(current_user, 'delete_artifact', obj_type='artifact', obj_id=id)
    flash('Նմուշը ջնջվեց')
    return redirect(url_for('index'))

@app.route('/artifact-image/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_artifact_image(image_id):
    # Only admins can delete images
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))

    artifact_image = ArtifactImage.query.get_or_404(image_id)
    artifact_id = artifact_image.artifact_id
    
    try:
        delete_image(artifact_image.image_url)
    except Exception:
        pass
    
    db.session.delete(artifact_image)
    db.session.commit()
    flash('Նկարը ջնջվեց')
    return redirect(url_for('edit_artifact', id=artifact_id))
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_artifact():
    # Only admins can add artifacts
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        # Year may be empty or non-numeric
        year_val = request.form.get('year')
        year = int(year_val) if year_val and year_val.isdigit() else None
        category = request.form.get('category')
        tags = request.form.get('tags')

        # Prefer uploaded file over external URL
        file = request.files.get('image_file')
        image_url = request.form.get('image_url')

        new_artifact = Artifact(
            name=name,
            description=description,
            year=year,
            category=category,
            tags=tags,
            user_id=current_user.id
        )

        if file and getattr(file, 'filename', ''):
            res = save_image(file)
            if res:
                new_artifact.image_url = res['filename']
                new_artifact.thumbnail_url = os.path.basename(res.get('thumbnail_path', ''))
            else:
                flash('Ընտրված ֆայլը անթույլատրելի է կամ մեծ չափի է')
                return redirect(url_for('add_artifact'))
        else:
            # fallback to external URL or provided value
            new_artifact.image_url = image_url

        db.session.add(new_artifact)
        db.session.flush()  # Ստանալ ID-ը առաջ նկարներ ավելացնել

        # Handle multiple uploaded images
        files = request.files.getlist('images')
        for file in files:
            if file and getattr(file, 'filename', ''):
                res = save_image(file)
                if res:
                    artifact_image = ArtifactImage(
                        artifact_id=new_artifact.id,
                        image_url=res['filename'],
                        thumbnail_url=os.path.basename(res.get('thumbnail_path', ''))
                    )
                    db.session.add(artifact_image)

        db.session.commit()
        # Log creation
        log_action(current_user, 'create_artifact', obj_type='artifact', obj_id=new_artifact.id)
        flash('Նմուշը հաջողությամբ ավելացվեց')
        return redirect(url_for('index'))
    
    return render_template('add.html')


@app.route('/exhibition/<int:id>')
def exhibition_detail(id):
    exhibition = Exhibition.query.get_or_404(id)
    return render_template('exhibition_detail.html', exhibition=exhibition, today=datetime.now().date())


@app.route('/admin/exhibition/<int:id>/clear_images', methods=['POST'])
@login_required
def clear_exhibition_images(id):
    # Only admins can clear images
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('exhibition_detail', id=id))

    exhibition = Exhibition.query.get_or_404(id)

    # Remove associated ArtifactImage rows and clear artifact image_url
    for artifact in list(exhibition.artifacts):
        # Delete additional images
        ArtifactImage.query.filter_by(artifact_id=artifact.id).delete()
        # Clear main image url
        artifact.image_url = None

    # Remove exhibition additional images
    ExhibitionImage.query.filter_by(exhibition_id=exhibition.id).delete()

    # Clear exhibition main image
    exhibition.image_url = None

    db.session.commit()
    flash('Ցուցադրության բոլոր նկարները ջնջվել են')
    # Log action
    try:
        log_action(current_user, 'clear_exhibition_images', obj_type='exhibition', obj_id=exhibition.id)
    except Exception:
        pass
    return redirect(url_for('exhibition_detail', id=id))

# Import search helpers after models and db have been created to avoid circular import issues
from search import search_artifacts, search_exhibitions

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    # Ֆիլտրերի ստացում
    filters = {
        'year_from': request.args.get('year_from'),
        'year_to': request.args.get('year_to'),
        'category': request.args.get('category'),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'status': request.args.get('status')
    }
    
    artifacts = []
    exhibitions = []

    if search_type in ['all', 'artifacts']:
        artifacts = search_artifacts(query, filters)

    if search_type in ['all', 'exhibitions']:
        exhibitions = search_exhibitions(query, filters)

    # If helpers returned SQLAlchemy Query objects, convert to lists so Jinja can use length and iterate safely
    def _to_list(maybe_query):
        try:
            if hasattr(maybe_query, 'all'):
                return maybe_query.all()
            if hasattr(maybe_query, '__iter__') and not isinstance(maybe_query, (str, bytes)):
                return list(maybe_query)
        except Exception:
            pass
        return maybe_query

    artifacts = _to_list(artifacts)
    exhibitions = _to_list(exhibitions)

    return render_template('search.html',
                         query=query,
                         search_type=search_type,
                         artifacts=artifacts,
                         exhibitions=exhibitions,
                         filters=filters)


@app.route('/admin/exhibition/<int:id>/add_image', methods=['POST'])
@login_required
def add_exhibition_image(id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('exhibition_detail', id=id))

    exhibition = Exhibition.query.get_or_404(id)
    image_url = request.form.get('image_url', '').strip()
    caption = request.form.get('caption', '').strip()
    if not image_url:
        flash('Խնդրում ենք տրամադրել նկարի URL')
        return redirect(url_for('exhibition_detail', id=id))

    ex_img = ExhibitionImage(exhibition_id=exhibition.id, image_url=image_url, caption=caption)
    db.session.add(ex_img)
    db.session.commit()
    flash('Նկարը հաջողությամբ ավելացվեց')
    try:
        log_action(current_user, 'add_exhibition_image', obj_type='exhibition', obj_id=exhibition.id)
    except Exception:
        pass
    return redirect(url_for('exhibition_detail', id=id))


@app.route('/admin/exhibition/<int:id>/delete_image/<int:img_id>', methods=['POST'])
@login_required
def delete_exhibition_image(id, img_id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('exhibition_detail', id=id))

    ex_img = ExhibitionImage.query.filter_by(id=img_id, exhibition_id=id).first_or_404()
    db.session.delete(ex_img)
    db.session.commit()
    flash('Նկարը ջնջվել է')
    try:
        log_action(current_user, 'delete_exhibition_image', obj_type='exhibition', obj_id=id)
    except Exception:
        pass
    return redirect(url_for('exhibition_detail', id=id))

@app.route('/add_exhibition', methods=['GET', 'POST'])
@login_required
def add_exhibition():
    # Only admins can add exhibitions
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('exhibitions'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        image_url = request.form['image_url']
        artifact_ids = request.form.getlist('artifacts')
        
        new_exhibition = Exhibition(
            title=title,
            description=description,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            image_url=image_url,
            user_id=current_user.id
        )
        
        if artifact_ids:
            artifacts = Artifact.query.filter(Artifact.id.in_(artifact_ids)).all()
            new_exhibition.artifacts.extend(artifacts)
        
        db.session.add(new_exhibition)
        db.session.commit()
        # Log new exhibition
        log_action(current_user, 'create_exhibition', obj_type='exhibition', obj_id=new_exhibition.id)
        flash('Ցուցադրությունը հաջողությամբ ավելավեց')
        return redirect(url_for('exhibitions'))
    
    artifacts = Artifact.query.all()
    return render_template('add_exhibition.html', artifacts=artifacts)


@app.route('/favorite/artifact/<int:id>', methods=['POST'])
@login_required
def favorite_artifact(id):
    artifact = Artifact.query.get_or_404(id)
    try:
        # check existing (dynamic relationship)
        exists = current_user.favorites_artifacts.filter_by(id=id).first() if hasattr(current_user.favorites_artifacts, 'filter_by') else (artifact in current_user.favorites_artifacts)
        if exists:
            current_user.favorites_artifacts.remove(artifact)
            action = 'removed'
        else:
            current_user.favorites_artifacts.append(artifact)
            action = 'added'
        db.session.commit()
        # count favorites
        try:
            count = artifact.favorited_by.count()
        except Exception:
            count = len(getattr(artifact, 'favorited_by', []))
        return jsonify({'status': action, 'count': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/favorite/exhibition/<int:id>', methods=['POST'])
@login_required
def favorite_exhibition(id):
    exhibition = Exhibition.query.get_or_404(id)
    try:
        exists = current_user.favorites_exhibitions.filter_by(id=id).first() if hasattr(current_user.favorites_exhibitions, 'filter_by') else (exhibition in current_user.favorites_exhibitions)
        if exists:
            current_user.favorites_exhibitions.remove(exhibition)
            action = 'removed'
        else:
            current_user.favorites_exhibitions.append(exhibition)
            action = 'added'
        db.session.commit()
        try:
            count = exhibition.favorited_by_exhibitions.count()
        except Exception:
            count = len(getattr(exhibition, 'favorited_by_exhibitions', []))
        return jsonify({'status': action, 'count': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500



# Թանգարանի ապագան էջի route

@app.route('/future-museum', methods=['GET', 'POST'])
def future_museum():
    global future_ideas
    if request.method == 'POST':
        idea_text = request.form.get('idea', '').strip()
        if idea_text:
            # Generate a new id
            new_id = max([i.id for i in future_ideas], default=0) + 1
            new_idea = Idea(id=new_id, text=idea_text, created_at=datetime.now())
            future_ideas.append(new_idea)
            flash('Շնորհակալություն ձեր գաղափարի համար!', 'success')
    return render_template('future_museum.html', ideas=future_ideas)

@app.route('/favorites')
@login_required
def favorites():
    # Show current user's favorite artifacts and exhibitions
    try:
        artifacts = current_user.favorites_artifacts.all() if hasattr(current_user.favorites_artifacts, 'all') else list(current_user.favorites_artifacts)
    except Exception:
        artifacts = list(current_user.favorites_artifacts)
    try:
        exhibitions = current_user.favorites_exhibitions.all() if hasattr(current_user.favorites_exhibitions, 'all') else list(current_user.favorites_exhibitions)
    except Exception:
        exhibitions = list(current_user.favorites_exhibitions)
    return render_template('favorites.html', artifacts=artifacts, exhibitions=exhibitions)



# --- MuseumQuestion model ---
class MuseumQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    answered_at = db.Column(db.DateTime, nullable=True)

# --- Ask the Museum route ---
@app.route('/ask-museum', methods=['GET', 'POST'])
def ask_museum():
    success = False
    if request.method == 'POST':
        question_text = request.form.get('question', '').strip()
        user_id = current_user.id if current_user.is_authenticated else None
        email = current_user.email if current_user.is_authenticated else request.form.get('email', '').strip()
        if question_text:
            q = MuseumQuestion(question=question_text, email=email, user_id=user_id)
            db.session.add(q)
            db.session.commit()
            success = True
        else:
            flash('Խնդրում ենք մուտքագրել հարցը։', 'error')
    # Show only current user's questions (if logged in), else none
    if current_user.is_authenticated:
        questions = MuseumQuestion.query.filter_by(user_id=current_user.id).order_by(MuseumQuestion.created_at.asc()).all()
    else:
        questions = []
    return render_template('ask_museum.html', questions=questions, success=success)

# --- Admin: Manage Future Museum Ideas ---
# For demo: use a simple in-memory list. Replace with DB model for production.
from datetime import datetime
from collections import namedtuple

Idea = namedtuple('Idea', ['id', 'text', 'created_at'])
future_ideas = [
    Idea(id=1, text='Ավելացնել վիրտուալ իրականության տուր', created_at=datetime(2026, 3, 20, 15, 30)),
    Idea(id=2, text='Կազմակերպել առցանց վարպետության դասեր', created_at=datetime(2026, 3, 21, 11, 0)),
]

@app.route('/admin/future-museum')
@login_required
def admin_future_museum():
    if not current_user.is_admin:
        flash('Այս էջը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
    return render_template('admin/future_museum.html', ideas=future_ideas)

@app.route('/admin/future-museum/delete/<int:idea_id>', methods=['POST'])
@login_required
def admin_delete_idea(idea_id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
    global future_ideas
    future_ideas = [idea for idea in future_ideas if idea.id != idea_id]
    flash('Գաղափարը ջնջվեց')
    return redirect(url_for('admin_future_museum'))




# Օգտատիրոջ հարցերի էջ
@app.route('/my-questions')
@login_required
def my_questions():
    questions = MuseumQuestion.query.filter_by(user_id=current_user.id).order_by(MuseumQuestion.created_at.desc()).all()
    return render_template('user/my_questions.html', questions=questions)

@app.route('/admin/questions', methods=['GET'])
@login_required
def admin_questions():
    if not current_user.is_admin:
        flash('Այս էջը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
    questions = MuseumQuestion.query.order_by(MuseumQuestion.created_at.desc()).all()
    return render_template('admin/ask_museum_admin.html', questions=questions)

@app.route('/admin/ask-museum/answer/<int:question_id>', methods=['POST'])
@login_required
def admin_answer_question(question_id):
    if not current_user.is_admin:
        flash('Այս գործողությունը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
    answer = request.form.get('answer', '').strip()
    q = MuseumQuestion.query.get_or_404(question_id)
    q.answer = answer
    q.answered_at = datetime.utcnow()
    db.session.commit()
    flash('Պատասխանը պահպանվեց։')
    return redirect(url_for('admin_questions'))


# --- Admin: User Chat ---
@app.route('/admin/user/<int:user_id>/chat', methods=['GET', 'POST'])
@login_required
def admin_user_chat(user_id):
    if not current_user.is_admin:
        flash('Այս էջը հասանելի է միայն ադմինիստրատորներին')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    questions = MuseumQuestion.query.filter_by(user_id=user_id).order_by(MuseumQuestion.created_at.asc()).all()
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        question_id = request.form.get('question_id', type=int)
        if answer and question_id:
            q = MuseumQuestion.query.get(question_id)
            if q and q.user_id == user_id:
                q.answer = answer
                q.answered_at = datetime.utcnow()
                db.session.commit()
                flash('Պատասխանը ուղարկվեց։')
            else:
                flash('Հարցը գտնված չէ կամ չի պատկանում այս օգտատիրոջը։', 'error')
        else:
            flash('Պահանջվում է հարց և պատասխան։', 'error')
        return redirect(url_for('admin_user_chat', user_id=user_id))
    return render_template('admin/user_chat.html', user=user, questions=questions)

# --- Flask app run block ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Գրանցված endpoint-ները:')
        print(app.url_map)
    app.run(debug=True)



