<template>
	<div id="wrapper" class="h-full w-full" v-on="handlers">
		<slot />
	</div>
</template>

<script setup>
import debounce from 'lodash/debounce';
import { useAuthStore } from '../stores/auth';
import { useRoute } from 'vue-router';
import { PRIVATE_ROUTES } from '../router';

const route = useRoute();
const auth = useAuthStore();

// Debounce func for performance
const refreshAuth = debounce(handleAuthRefresh, 350, { leading: true });

const handlers = {
	click: refreshAuth,
	keydown: refreshAuth,
	keypress: refreshAuth,
	keyup: refreshAuth,
	touchstart: refreshAuth,
	touchend: refreshAuth,
	touchcancel: refreshAuth,
	touchmove: refreshAuth,
	scroll: refreshAuth,
	submit: refreshAuth,
};

function handleAuthRefresh() {
	const isAuthRoute = PRIVATE_ROUTES.includes(route);

	const now = Date.now();
	const difference = auth.accessToken.expires - now;

	/* c8 ignore next 6 */
	if (difference > 0) {
		console.debug({
			secondsUntilRefreshOnUserActivity: (difference - 60000) / 1000,
			secondsUntilInactivityLogout: difference / 1000,
		});
	}

	// User's token is about to expire, update it.
	if (difference <= 60 * 1000 && difference > 0) {
		return auth.refreshAccessToken();
		// User's token is expired, log out.
	} else if (difference <= 0 && auth.userId) {
		return auth.logout(isAuthRoute);
	}
}
</script>
