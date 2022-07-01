from app import db

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), unique=True)
    group_link = db.Column(db.String(120), unique=True)
    sign_up_date = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, group_id, group_link):
        self.group_id = group_id
        self.group_link = group_link
        self.sign_up_date = db.func.now()

    def __repr__(self):
        return '<Group %r>' % self.group_id


class Subscription(db.Model):
    pass

class Tokens(db.Model):
    pass

class BiggestBuyCampaign(db.Model):
    pass

class RaffleCampaign(db.Model):
    pass

class ActiveCompetitions(db.Model):
    pass

class SupportedChain(db.Model):
    pass

class Admins(db.Model):
    pass

class Wallets(db.Model):
    pass
