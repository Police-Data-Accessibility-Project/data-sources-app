/**
 * Gets enabled / disabled status for features.
 *
 * @param {'ENHANCED_SEARCH' | 'AUTHENTICATE' | 'CREATE_RECORDS'} featureName Name of V2 feature to check
 * @returns {boolean} Whether the feature is enabled or not
 */
export function getIsV2FeatureEnabled(featureName) {
	console.debug({
		featureName,
		value: import.meta.env[`VITE_V2_FEATURE_${featureName}`],
		bool: import.meta.env[`VITE_V2_FEATURE_${featureName}`] === 'enabled',
	});
	return import.meta.env[`VITE_V2_FEATURE_${featureName}`] === 'enabled';
}
