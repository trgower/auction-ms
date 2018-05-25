from app import db, app
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())

    # Other information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')

    auctions = db.relationship('Auctions', backref='user', lazy='dynamic')
    bids = db.relationship('Bids', backref='user', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='user', lazy='dynamic')
    alerts = db.relationship('Alerts', backref='user', lazy='dynamic')


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)
user_manager.enable_change_username = False


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    slot = db.Column(db.String(16))
    reqlevel = db.Column(db.Integer)
    reqjob = db.Column(db.Integer)
    reqstr = db.Column(db.Integer)
    reqint = db.Column(db.Integer)
    reqdex = db.Column(db.Integer)
    reqluk = db.Column(db.Integer)
    watk = db.Column(db.Integer)
    matk = db.Column(db.Integer)
    int = db.Column(db.Integer)
    str = db.Column(db.Integer)
    luk = db.Column(db.Integer)
    dex = db.Column(db.Integer)
    eva = db.Column(db.Integer)
    acc = db.Column(db.Integer)
    atkspeed = db.Column(db.Integer)
    wdef = db.Column(db.Integer)
    mdef = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    mp = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    jump = db.Column(db.Integer)
    price = db.Column(db.Integer)
    tuc = db.Column(db.Integer)

    def get_dict(self):
        return {'watk': self.watk, 'matk': self.matk, 'int': self.int, 'str': self.str, 'luk': self.luk,
                'dex': self.dex, 'eva': self.eva, 'acc': self.acc,
                'wdef': self.wdef, 'mdef': self.mdef, 'hp': self.hp, 'mp': self.mp, 'speed': self.speed,
                'jump': self.jump, 'slots': self.tuc, 'upgrades': 0}


class Scroll(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    success = db.Column(db.Integer)
    cursed = db.Column(db.Integer)
    watk = db.Column(db.Integer)
    matk = db.Column(db.Integer)
    int = db.Column(db.Integer)
    str = db.Column(db.Integer)
    luk = db.Column(db.Integer)
    dex = db.Column(db.Integer)
    eva = db.Column(db.Integer)
    acc = db.Column(db.Integer)
    wdef = db.Column(db.Integer)
    mdef = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    mp = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    jump = db.Column(db.Integer)

    def get_dict(self):
        return {'watk': self.watk, 'matk': self.matk, 'int': self.int, 'str': self.str, 'luk': self.luk,
                'dex': self.dex, 'eva': self.eva, 'acc': self.acc,
                'wdef': self.wdef, 'mdef': self.mdef, 'hp': self.hp, 'mp': self.mp, 'speed': self.speed,
                'jump': self.jump}


class Potions(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    time = db.Column(db.Integer)
    watk = db.Column(db.Integer)
    matk = db.Column(db.Integer)
    eva = db.Column(db.Integer)
    acc = db.Column(db.Integer)
    wdef = db.Column(db.Integer)
    mdef = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    mp = db.Column(db.Integer)
    hpR = db.Column(db.Integer)
    mpR = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    jump = db.Column(db.Integer)
    poison = db.Column(db.Integer)
    seal = db.Column(db.Integer)
    darkness = db.Column(db.Integer)
    weakness = db.Column(db.Integer)
    curse = db.Column(db.Integer)
    price = db.Column(db.Integer)


class Strings(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    type = db.Column(db.Integer)
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.Text)

    auctions = db.relationship('Auctions', backref='strings', lazy='dynamic')


class Projectiles(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    reqLevel = db.Column(db.Integer)
    watk = db.Column(db.Integer)
    slotMax = db.Column(db.Integer)
    unitPrice = db.Column(db.Float)
    price = db.Column(db.Integer)


class Auctions(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('strings.id'), index=True)
    starting_bid = db.Column(db.Integer, default=0)
    bid = db.Column(db.Integer, default=0)
    min_bid_inc = db.Column(db.Integer, default=0)
    reserve = db.Column(db.Integer, default=0)
    fm_channel = db.Column(db.Integer, default=0, index=True)
    fm_door = db.Column(db.Integer, default=0, index=True)
    length = db.Column(db.Integer)
    posted = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    transaction_step = db.Column(db.Integer, default=-1)
    buyer_id = db.Column(db.Integer, default=-1)
    item_quality = db.Column(db.Integer, default=0)
    sc_offered = db.Column(db.Integer, default=0)

    watk = db.Column(db.Integer, default=0)
    matk = db.Column(db.Integer, default=0)
    int = db.Column(db.Integer, default=0)
    str = db.Column(db.Integer, default=0)
    luk = db.Column(db.Integer, default=0)
    dex = db.Column(db.Integer, default=0)
    eva = db.Column(db.Integer, default=0)
    acc = db.Column(db.Integer, default=0)
    wdef = db.Column(db.Integer, default=0)
    mdef = db.Column(db.Integer, default=0)
    hp = db.Column(db.Integer, default=0)
    mp = db.Column(db.Integer, default=0)
    speed = db.Column(db.Integer, default=0)
    jump = db.Column(db.Integer, default=0)
    slots = db.Column(db.Integer, default=0)
    upgrades = db.Column(db.Integer, default=0)

    bids = db.relationship('Bids', backref='auctions', lazy='dynamic', order_by='desc(Bids.amount)', cascade="all, delete-orphan")
    comments = db.relationship('Comments', backref='auctions', lazy='dynamic', cascade="all, delete-orphan")
    watchers = db.relationship('Watchlists', backref='auctions', lazy='dynamic', cascade="all, delete-orphan")


class Bids(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    bidder_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), index=True)
    amount = db.Column(db.Integer)
    posted = db.Column(db.DateTime())


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    commenter_id = db.Column(db.Integer)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), index=True)
    message = db.Column(db.Text)
    posted = db.Column(db.DateTime())


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    reviewer = db.Column(db.Integer, index=True)
    reviewee = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    auction_id = db.Column(db.Integer, index=True)
    score = db.Column(db.Integer)
    message = db.Column(db.Text)
    posted = db.Column(db.DateTime())


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    sender_id = db.Column(db.Integer, index=True)
    recp_id = db.Column(db.Integer, index=True)
    message = db.Column(db.Text)
    sent = db.Column(db.DateTime())


class Conversations(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    conversant = db.Column(db.Integer, index=True)
    created = db.Column(db.DateTime())
    last_msg = db.Column(db.DateTime())
    last_read = db.Column(db.DateTime())


class Watchlists(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    watcher_id = db.Column(db.Integer, index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), index=True)
    posted = db.Column(db.DateTime())


class Alerts(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    category = db.Column(db.String)
    message = db.Column(db.String)


class HotAuctions(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    auction_id = db.Column(db.Integer, index=True)