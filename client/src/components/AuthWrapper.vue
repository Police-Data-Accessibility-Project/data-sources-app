<template>
	<div id="wrapper" class="h-full w-full" v-on="handlers">
		<slot />
	</div>
</template>

<script setup>
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const route = useRoute();
const { refreshAccessToken, setRedirectTo, logout, tokens, isAuthenticated } =
	useAuthStore();

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
	const now = Date.now();
	const differenceFromAccess = tokens.accessToken.expires - now;
	const isExpiredAccess = differenceFromAccess <= 0;
	const shouldRefresh = differenceFromAccess <= 60 * 1000;
	const shouldLogout = isExpiredAccess;

	// User's token is about to expire, so we refresh it.g
	if (shouldRefresh && isAuthenticated) {
		return refreshAccessToken();
		// User's tokens are all expired, log out.
	} else if (shouldLogout && isAuthenticated) {
		setRedirectTo(route);
		return logout();
	} else return;
}
</script>
