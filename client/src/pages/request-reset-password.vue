<template>
	<main class="pdap-flex-container" :class="{ 'mx-auto max-w-2xl': !success }">
		<h1>Request a link to reset your password</h1>
		<template v-if="success">
			<p data-test="success-subheading">
				We sent you an email with a link to reset your password. Please follow
				the link in the email to proceed
			</p>
		</template>

		<template v-else>
			<FormV2
				id="reset-password"
				ref="formRefRequest"
				data-test="reset-password-form"
				class="flex flex-col"
				name="reset-password"
				:error="error"
				:schema="VALIDATION_SCHEMA_REQUEST_PASSWORD"
				@submit="onSubmitRequestReset"
			>
				<InputText
					id="email"
					autocomplete="email"
					data-test="email"
					name="email"
					label="Email"
					placeholder="Your email address"
				/>
				<Button class="max-w-full" :is-loading="loading" type="submit">
					Request password reset
				</Button>
			</FormV2>
		</template>
	</main>
</template>

<script setup>
import { Button, FormV2, InputText } from 'pdap-design-system';
import { useUserStore } from '@/stores/user';
import { ref, onMounted } from 'vue';

// Constants
const VALIDATION_SCHEMA_REQUEST_PASSWORD = [
	{
		name: 'email',
		validators: {
			required: {
				value: true,
			},
			email: {
				message: 'Please provide your email address',
				value: true,
			},
		},
	},
];

// Stores
const user = useUserStore();

// Reactive vars
const formRefRequest = ref();
const error = ref(undefined);
const loading = ref(false);
const success = ref(false);

// Lifecycle hooks
onMounted(() => {
	formRefRequest.value?.setValues({ email: user.email });
});
// Functions
async function onSubmitRequestReset(formValues) {
	try {
		loading.value = true;
		const { email } = formValues;
		await user.requestPasswordReset(email);
		success.value = true;
	} catch (err) {
		error.value = err.message;
	} finally {
		loading.value = false;
	}
}
</script>
