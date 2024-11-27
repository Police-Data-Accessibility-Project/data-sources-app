<template>
	<div id="wrapper" class="h-full w-full" v-on="handlers">
		<slot />
	</div>
</template>

<script setup>
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();

const { refreshAccessToken, signOut, tokens, isAuthenticated } = useAuthStore();
const user = useUserStore();

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
	const now = new Date().getTime();
	const differenceFromAccess = tokens.accessToken.expires - now;
	const isExpiredAccess = differenceFromAccess <= 0;
	const shouldRefresh = differenceFromAccess <= 60 * 1000 && isAuthenticated();
	const shouldLogout = isExpiredAccess && !!user.id;

	// User's token is about to expire, so we refresh it.
	if (shouldRefresh) {
		return refreshAccessToken();
		// User's tokens are all expired, log out.
	} else if (shouldLogout) {
		signOut();
		if (route?.meta?.auth) router.replace('/sign-in');
	} else return;
}
</script>
