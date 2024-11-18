import { onMounted } from 'vue';

/** Sets theme as class to document.documentElement
 * This is only necessary because `vue3-toastify` expects global themes to be set this way.
 * 🙄 https://github.com/jerrywu001/vue3-toastify/blob/96706e8399c336bd1d8c458cf872b6df395352a0/src/utils/tools.ts#L60-L62*/
export default function useThemePreference() {
	const applyTheme = (newTheme) => {
		// Remove any existing theme classes
		document.documentElement.classList.remove('light', 'dark');
		// Add the new theme class
		document.documentElement.classList.add(newTheme);
	};

	const initializeTheme = () => {
		// Check system preference
		const prefersDark = window.matchMedia(
			'(prefers-color-scheme: dark)',
		).matches;
		applyTheme(prefersDark ? 'dark' : 'light');
	};

	// Watch for system theme changes
	const setupThemeListener = () => {
		const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

		mediaQuery.addEventListener('change', (e) => {
			const newTheme = e.matches ? 'dark' : 'light';
			// Only apply system preference if no stored preference exists
			if (!localStorage.getItem('theme')) {
				applyTheme(newTheme);
			}
		});
	};

	onMounted(() => {
		initializeTheme();
		setupThemeListener();
	});

	return true;
}
