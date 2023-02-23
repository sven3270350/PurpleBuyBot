from datetime import datetime
from typing import List, TypedDict
from models import db, Campaigns

# Types
class CampaignWinners(TypedDict):
    id: int
    start: datetime
    end: datetime
    winner: str
    contest: str
    prize: str
   
 
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
        try:
            constest: Campaigns = Campaigns.query.filter_by(
                id=campaign_id).first()
            constest.end_time = datetime.now()
            constest.start_time = datetime.now()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print("[CampaignService::update_campaign_end_time_by_id]", e)
            return False

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

    def get_campaign_winners(self, group_id)->List[CampaignWinners]:
        stmt = f'''
            UPDATE public.campaigns
            SET
                campaign_winner = (
                    CASE
                        WHEN campaigns.campaing_type = 'Biggest Buy' THEN (
                            SELECT buyer_address
                            FROM (
                                    SELECT
                                        buyer_address,
                                        RANK() OVER (
                                            ORDER BY
                                                t.amount DESC
                                        ) AS campaignRank
                                    FROM (
                                            SELECT
                                                buyer_address,
                                                SUM(buyer_amount) AS amount
                                            FROM public.transactions
                                            WHERE
                                                campaign_id = campaigns.id
                                            GROUP BY
                                                buyer_address
                                        ) AS t
                                    ORDER BY campaignRank
                                    LIMIT
                                        1
                                ) as w
                        )
                        WHEN campaing_type = 'Last Buy' THEN (
                            SELECT buyer_address
                            FROM
                                public.transactions
                            WHERE
                                campaign_id = campaigns.id
                            ORDER BY id DESC
                            LIMIT
                                1
                        )
                        WHEN campaing_type = 'Raffle' THEN (
                            SELECT buyer_address
                            FROM public.transactions
                            WHERE
                                campaign_id = campaigns.id
                            ORDER BY RANDOM()
                            LIMIT
                                1
                        )
                        ELSE 'Not Available'
                    END
                )
            WHERE campaigns.id IN (
                    SELECT id
                    From public.campaigns
                    WHERE
                        group_id = '-1001743891337'
                    ORDER BY id DESC
                    LIMIT
                        5
                )
                AND campaigns.campaign_winner ISNULL;

            SELECT
                id,
                start_time as "start",
                end_time as "end",
                campaign_winner as winner,
                campaing_type as contest,
                prize
            FROM public.campaigns
            WHERE
                group_id = '{group_id}'
            ORDER BY id DESC
            LIMIT 5;
        '''
        return list(db.engine.execute(stmt))
