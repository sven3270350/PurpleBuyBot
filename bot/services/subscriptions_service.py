
from models import db, Subscription, SubscriptionType


class SubscriptionService:

    def get_group_pending_subscription(self, group_id):
        subscription = Subscription.query.filter_by(
            group_id=group_id, status='pending').first()
        return subscription

    def get_subscription_plans(self):
        plans = SubscriptionType.query.all()
        return plans

    def get_subscription_plan_by_id(self, plan_id):
        plan = SubscriptionType.query.filter_by(id=plan_id).first()
        return plan

    def get_active_active_subscription_by_group_id(self, group_id):
        stmt = f'''
        SELECT 
        st.subscription_type,
        ss.start_date, ss.end_date,
        ss.number_of_countable_subscriptions AS total,
        ss.is_life_time_subscription AS for_life,
        CASE 
            WHEN ss.end_date >= NOW() THEN 'active'
            ELSE 'inactive'
        END AS status
        FROM PUBLIC.subscription ss
        JOIN public.subscription_type st
        ON st.id = ss.subscription_type_id
        WHERE ss.group_id = '{group_id}' AND ss.end_date >= NOW();
        '''
        return list(db.engine.execute(stmt))

    def get_active_ad(self):
        stmt = '''
          SELECT advert FROM public.advertisement WHERE "isActive" = true;
        '''
        return list(db.engine.execute(stmt))

    def has_active_subscription(self, group_id):
        subscription: list = self.get_active_active_subscription_by_group_id(
            group_id)
        if subscription:
            return True
        else:
            return False

    def get_ad(self, group_id):
        ad = ""

        try:
            if not self.has_active_subscription(group_id):
                ad = self.get_active_ad()[0]['advert']
        except Exception as e:
            print(e)

        return ad
