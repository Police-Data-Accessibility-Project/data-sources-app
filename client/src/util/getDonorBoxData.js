import axios from 'axios';

const DONOR_BOX_PROXY = `https://thingproxy.freeboard.io/fetch/https://donorbox.org/api/v1/campaigns`;
const CAMPAIGN_ID = import.meta.env.VITE_DONORBOX_CAMPAIGN_ID;

export default async function getDonorBoxData() {
	const donorbox_api_key = import.meta.env.VITE_DONORBOX_API_KEY;
	const donorbox_email = import.meta.env.VITE_DONORBOX_EMAIL;
	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Basic ${btoa(donorbox_email + ':' + donorbox_api_key)}`,
	};

	try {
		const response = await axios.get(DONOR_BOX_PROXY, {
			headers,
			params: {
				id: CAMPAIGN_ID,
			},
		});

		return {
			goal: response.data[0].goal_amt,
			raised: response.data[0].total_raised,
		};
	} catch (error) {
		console.error('Error fetching donation data:', error);
	}
}
