try:
    from bot.app import db
except ImportError:
    from app import db


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), unique=True)
    group_title = db.Column(db.Text)
    username = db.Column(db.Text)
    sign_up_date = db.Column(db.DateTime, default=db.func.now())
    buy_icon = db.Column(db.String(2), default="🟢")
    buy_media = db.Column(db.Text)
    subscriptions = db.relationship(
        'Subscription', backref='group', lazy='dynamic')
    tracked_tokens = db.relationship(
        'TrackedToken', backref='group', lazy='dynamic')
    campaigns = db.relationship(
        'Campaigns', backref='group', lazy='dynamic')
    wallet = db.relationship(
        'Wallet', back_populates="group", uselist=False)

    def __init__(self, group_id, group_title, username):
        self.group_id = group_id
        self.group_title = group_title
        self.username = username
        self.sign_up_date = db.func.now()

    def __repr__(self):
        return '<Group %r>' % self.group_link


class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), db.ForeignKey('group.group_id'))
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    subscription_type_id = db.Column(
        db.Integer, db.ForeignKey('subscription_type.id'))
    payment_chain_id = db.Column(
        db.Integer, db.ForeignKey('supported_chain.chain_id'))
    tx_hash = db.Column(db.String(120), unique=True)
    status = db.Column(db.String(120))
    start_date = db.Column(db.DateTime, default=db.func.now())
    end_date = db.Column(db.DateTime)
    number_of_countable_subscriptions = db.Column(db.Integer)
    is_life_time_subscription = db.Column(db.Boolean)
    expected_amount_in_native_wei = db.Column(db.BigInteger)

    def __repr__(self):
        return '<Subscription %r>' % f"{self.group_id}_{self.id}"


class SubscriptionType(db.Model):
    __tablename__ = 'subscription_type'
    id = db.Column(db.Integer, primary_key=True)
    subscription_type = db.Column(db.String(80))
    usd_price = db.Column(db.Float)

    def __repr__(self):
        return '<SubscriptionType %r>' % self.subscription_type


class TrackedToken(db.Model):
    __tablename__ = 'tracked_token'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(100))
    token_name = db.Column(db.String(100))
    token_symbol = db.Column(db.String(20))
    token_decimals = db.Column(db.Integer)
    circulating_supply = db.Column(db.Float)
    pair_address = db.Column(db.String(100))
    active_tracking = db.Column(db.Boolean, default=True)
    chain = db.relationship(
        'SupportedChain', secondary='token_chains', backref='tracked_token')
    pair = db.relationship(
        'SupportedPairs', secondary='token_pairs', backref='tracked_token')
    dex = db.relationship(
        'SupportedExchange', secondary='token_dexs', backref='tracked_token')
    group_id = db.Column(db.String(80), db.ForeignKey('group.group_id'))

    def __repr__(self):
        return '<TrackedToken %r>' % self.token_name


class Campaigns(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), db.ForeignKey('group.group_id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    count_down = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    campaign_winner = db.Column(db.String(100))
    min_amount = db.Column(db.Float)
    campaing_type = db.Column(db.String(120))
    prize = db.Column(db.Text)
    transactions = db.relationship(
        'Transactions', backref='campaign', lazy='dynamic')

    def __repr__(self):
        return '<Campaigns %r>' % f"{self.campaing_type}_{self.group_id}_{self.id}"


class SupportedChain(db.Model):
    __tablename__ = 'supported_chain'
    id = db.Column(db.Integer, primary_key=True)
    chain_name = db.Column(db.String(20))
    chain_id = db.Column(db.Integer, unique=True, nullable=False)
    native_symbol = db.Column(db.String(20))
    exchanges = db.relationship(
        'SupportedExchange', backref='supported_chain')
    pairs = db.relationship(
        'SupportedPairs', backref='supported_chain')


class SupportedExchange(db.Model):
    __tablename__ = 'supported_exchange'
    id = db.Column(db.Integer, primary_key=True)
    exchange_name = db.Column(db.String(20))
    router_address = db.Column(db.String(100), unique=True, nullable=False)
    factory_address = db.Column(db.String(100), unique=True, nullable=False)
    chain_id = db.Column(
        db.Integer, db.ForeignKey('supported_chain.chain_id'))


class SupportedPairs(db.Model):
    __tablename__ = 'supported_pairs'
    id = db.Column(db.Integer, primary_key=True)
    pair_name = db.Column(db.String(20))
    pair_address = db.Column(db.String(100), unique=True, nullable=False)
    chain_id = db.Column(
        db.Integer, db.ForeignKey('supported_chain.chain_id'))


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(80))
    admin_username = db.Column(db.String(80))

    def __repr__(self):
        return '<Admin %r>' % self.admin_username


class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(100))
    wallet_private_key = db.Column(db.String(100))
    group_id = db.Column(db.String(80), db.ForeignKey('group.group_id'))
    group = db.relationship("Group", back_populates="wallet")

    def __init__(self, wallet_address, wallet_private_key):
        self.wallet_address = wallet_address
        self.wallet_private_key = wallet_private_key

    def __repr__(self):
        return '<Wallet %r>' % self.wallet_address


class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(
        db.Integer, db.ForeignKey('campaigns.id'))
    buyer_address = db.Column(db.String(100))
    buyer_amount = db.Column(db.Float)
    transaction_link = db.Column(db.String(100))
    transaction_chain = db.Column(db.String(20))
    cmapaign_type = db.Column(db.String(100))
    group_id = db.Column(db.String(80), db.ForeignKey('group.group_id'))

    def __repr__(self):
        return '<Transactions %r>' % f"{self.group_id}_{self.biggest_buy_campaign_id}_{self.id}"


class Advertisement(db.Model):
    __tablename__ = "advertisement"
    id = db.Column(db.Integer, primary_key=True)
    advert = db.Column(db.Text, nullable=False)
    isActive = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Advertisement %r>' % self.advert


#  Association tables
token_chains = db.Table('token_chains',
                        db.metadata,
                        db.Column('token_id', db.Integer,
                                  db.ForeignKey('tracked_token.id')),
                        db.Column('chain_id', db.Integer,
                                  db.ForeignKey('supported_chain.id'))
                        )


token_dexs = db.Table('token_dexs',
                      db.metadata,
                      db.Column('token_id', db.Integer,
                                db.ForeignKey('tracked_token.id')),
                      db.Column('exchange_id', db.Integer,
                                db.ForeignKey('supported_exchange.id'))
                      )


token_pairs = db.Table('token_pairs',
                       db.metadata,
                       db.Column('token_id', db.Integer,
                                 db.ForeignKey('tracked_token.id')),
                       db.Column('pair_id', db.Integer,
                                 db.ForeignKey('supported_pairs.id')),
                       )
