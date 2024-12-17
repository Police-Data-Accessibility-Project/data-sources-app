/**
 * Endpoints by namespace.
 */
export const ENDPOINTS = {
	AUTH: {
		API_KEY: 'api-key',
		LINK_TO_GITHUB: 'link-to-github',
		LOGIN: 'login',
		REFRESH_SESSION: 'refresh-session',
		REQUEST_RESET_PASSWORD: 'reset-reset-password',
		RESEND_VALIDATION_EMAIL: 'resend-validation-email',
		RESET_PASSWORD: 'reset-password',
		RESET_TOKEN_VALIDATION: 'reset-token-validation',
		SIGNUP: 'signup',
		VALIDATE_EMAIL: 'validate-email',
	},
	CHECK: {
		UNIQUE_URL: 'unique-url',
	},
	DATA_REQUESTS: {
		ID: {
			RELATED_LOCATIONS: 'related-locations',
			RELATED_SOURCES: 'related-sources',
			WITHDRAW: 'withdraw',
		},
	},
	DATA_SOURCES: {
		ID: {
			RELATED_AGENCIES: 'related-agencies',
		},
	},
	LOCATIONS: {
		ID: {
			DATA_REQUESTS: 'data-requests',
		},
	},
	OAUTH: {
		GITHUB: 'github',
		LINK_TO_GITHUB: 'link-to-github',
		LOGIN_WITH_GITHUB: 'login-with-github',
	},
	SEARCH: {
		FOLLOW: 'follow',
		RESULTS: 'search-location-and-record-type',
	},
	USER: {
		DATA_REQUESTS: 'data-requests',
		RECENT_SEARCHES: 'recent-searches',
		ID: {
			UPDATE_PASSWORD: 'update-password',
		},
	},
};
