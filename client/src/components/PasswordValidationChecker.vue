<template>
	<ul class="text-med mb-8 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
		<span class="w-full">
			Passwords must contain at least
			<span
				:class="{
					valid: validation.fullLength,
				}"
				>8 characters</span
			>
			and include:
		</span>
		<li
			:class="{
				valid: validation.uppercase,
			}"
		>
			<FontAwesomeIcon
				:icon="validation.uppercase ? faCheckCircle : faDotCircle"
			/>
			1 uppercase letter
		</li>
		<li
			:class="{
				valid: validation.lowercase,
			}"
		>
			<FontAwesomeIcon
				:icon="validation.lowercase ? faCheckCircle : faDotCircle"
			/>
			1 lowercase letter
		</li>
		<li
			:class="{
				valid: validation.number,
			}"
		>
			<FontAwesomeIcon
				:icon="validation.number ? faCheckCircle : faDotCircle"
			/>
			1 number
		</li>
		<li
			:class="{
				valid: validation.specialCharacter,
			}"
		>
			<FontAwesomeIcon
				:icon="validation.specialCharacter ? faCheckCircle : faDotCircle"
			/>
			1 special character
		</li>
	</ul>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import {
	faCheckCircle,
	faDotCircle,
} from '@fortawesome/free-regular-svg-icons';
import { reactive } from 'vue';

const validation = reactive({
	fullLength: false,
	lowercase: false,
	number: false,
	specialCharacter: false,
	uppercase: false,
});

function updatePasswordValidation(password) {
	// Length
	if (password.length >= 8) {
		validation.fullLength = true;
	} else {
		validation.fullLength = false;
	}

	// Test uppercase
	if (/[A-Z]/gm.test(password)) {
		validation.uppercase = true;
	} else {
		validation.uppercase = false;
	}

	// Test lowercase
	if (/[a-z]/gm.test(password)) {
		validation.lowercase = true;
	} else {
		validation.lowercase = false;
	}

	// Test number
	if (/[0-9]/gm.test(password)) {
		validation.number = true;
	} else {
		validation.number = false;
	}

	// Test special char
	if (/[#?!@$%^&*-]/gm.test(password)) {
		validation.specialCharacter = true;
	} else {
		validation.specialCharacter = false;
	}
}

function isPasswordValid() {
	if (!Object.values(validation).every(Boolean)) {
		// error.value = 'Password is not valid';
		return false;
	} else {
		return true;
	}
}

defineExpose({
	isPasswordValid,
	updatePasswordValidation,
});

// onBeforeUpdate(() => {
// 	updatePasswordValidation(passwordComputed);
// });
</script>

<style scoped>
li {
	@apply flex gap-3 items-center sm:grow-0 sm:shrink sm:basis-[45%] transition-opacity duration-300;
}

li:not(.valid) {
	@apply opacity-70;
}

li .svg-inline--fa {
	@apply transition-colors duration-300;
}

li.valid {
	@apply opacity-100;
}

li.valid .svg-inline--fa,
span.valid {
	@apply text-green-700 dark:text-green-300;
}
</style>
