from datetime import datetime
from models import db, Campaigns


class CampaignService:

    # create a new campaigns,
    # get all campaigns,
    # get active campaigns,
    # get campaigns transactions
    # get campaigns winners

    def get_scheduled_campaigns(self, group_id):

        pass

    def get_all_campaigns(self):
        pass

    def get_active_campaigns(self, group_id):
        contest: Campaigns = Campaigns.query.filter_by(
            group_id=group_id).filter(Campaigns.end_time >= datetime.now()).all()
        return contest

    def update_campaign_end_time_by_id(self, campaign_id):
        constest: Campaigns = Campaigns.query.filter_by(
            id=campaign_id).first()
        constest.end_time = datetime.now()
        constest.start_time = datetime.now()
        db.session.commit()
        return constest

    def get_active_campaigns_count(self, group_id):
        stmt = f'''
        SELECT COUNT(*) 
	 	FROM public.campaigns
        WHERE 
		public.campaigns.end_time >= NOW()
		AND public.campaigns.group_id = '{group_id}';
        '''
        return list(db.engine.execute(stmt))[0][0]

    def get_campaign_transactions(self, campaign_id):
        pass

    def get_campaign_winners(self, campaign_id):
        pass
