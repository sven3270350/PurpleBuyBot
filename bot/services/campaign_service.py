from models import db


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
