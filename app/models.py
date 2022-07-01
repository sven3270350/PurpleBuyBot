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
     id = db.Column(db.Integer, primary_key=True)

class Tokens(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class BiggestBuyCampaign(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class RaffleCampaign(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class ActiveCompetitions(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class SupportedChain(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class Admins(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class Wallets(db.Model):
     id = db.Column(db.Integer, primary_key=True)

class Transactions(db.Model):
     id = db.Column(db.Integer, primary_key=True)
