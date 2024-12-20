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
import { refreshTokens, signOut } from '@/api/auth';
import { updateGlobalOptions, globalOptions } from 'vue3-toastify';
import { watch, ref, onMounted } from 'vue';

const isHeaderVisible = ref(true);

watch(isHeaderVisible, (visible) => {
	updateGlobalOptions({
		...globalOptions.value,
		style: {
			...globalOptions.style,
			top: visible ? '120px' : '20px',
		},
		theme: 'auto',
	});
});

onMounted(() => {
	const observer = new IntersectionObserver(
		([entry]) => {
			isHeaderVisible.value = entry.isIntersecting;
		},
		{ threshold: 0 },
	);

	const navbar = document.querySelector('.pdap-header');
	if (navbar) {
		observer.observe(navbar);
	}
});

const route = useRoute();
const router = useRouter();

const auth = useAuthStore();
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
	const differenceFromAccess = auth.tokens.accessToken.expires - now;
	const isExpiredAccess = differenceFromAccess <= 0;
	const shouldRefresh =
		differenceFromAccess <= 60 * 1000 && auth.isAuthenticated();
	const shouldLogout = isExpiredAccess && !!user.id;

	// User's token is about to expire, so we refresh it.
	if (shouldRefresh) {
		return refreshTokens();
		// User's tokens are all expired, log out.
	} else if (shouldLogout) {
		signOut();
		if (route?.meta?.auth) router.replace('/sign-in');
	} else return;
}
</script>
