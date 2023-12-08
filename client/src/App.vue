<template>
	<AppHeader />
	<router-view></router-view>
	<AppFooter />
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

export default {
	name: 'App',
	components: {
		AppHeader,
		AppFooter,
	},
};
</script>

<style>
body {
	background-color: #fffbfa;
	font-family: 'Libre Franklin', sans-serif;
	color: #000;
	font-size: 26px;
	line-height: 1.5;
	font-weight: 300;
}

h1 {
	margin-top: 50px;
	margin-bottom: 15px;
	font-size: 42px;
	line-height: 1.2;
	font-weight: 500;
}

h2 {
	margin-top: 32px;
	margin-bottom: 15px;
	font-size: 32px;
	line-height: 1.2;
	font-weight: 700;
}

h3 {
	margin-top: 30px;
	margin-bottom: 10px;
	font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
		Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
	color: #512a4f;
	font-size: 18px;
	line-height: 1.2;
	font-weight: 800;
	letter-spacing: 0.1em;
	text-transform: uppercase;
}

h4 {
	margin-top: 10px;
	margin-bottom: 10px;
	font-size: 18px;
	line-height: 1.2;
	font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
		Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
	color: #512a4f;
	font-weight: 600;
	letter-spacing: 0.07em;
	text-transform: uppercase;
}

h5 {
	margin-top: 10px;
	margin-bottom: 10px;
	font-family: 'Libre Franklin', sans-serif;
	font-size: 26px;
	line-height: 1.2;
	font-style: italic;
	font-weight: 300;
}

h6 {
	margin-top: 10px;
	margin-bottom: 10px;
	font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
		Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
	font-size: 18px;
	line-height: 1.2;
	font-weight: 300;
	letter-spacing: 3px;
	text-transform: uppercase;
}

h6 a,
h5 a,
h4 a,
h3 a,
h2 a,
h1 a {
	text-decoration: none;
}

ul,
p,
li {
	max-width: 43ch;
}

p {
	margin-bottom: 15px;
}

ul {
	padding-inline-start: 0.75em;
}

a {
	color: #d5a23c;
	text-decoration-thickness: 6%;
	text-underline-offset: 5%;
}

a:hover {
	filter: brightness(0.85);
}

strong {
	font-weight: 600;
}

.small p,
.small li,
p.small,
.small a,
.small label {
	font-size: 20px;
}

.button {
	width: auto;
	margin-top: 5px;
	margin-bottom: 5px;
	padding-right: 25px;
	padding-left: 25px;
	background-color: #d5a23c;
	font-size: 20px;
	font-weight: 600;
	text-align: center;
	cursor: pointer;
}

@media (prefers-color-scheme: dark) {
	body {
		background-color: #000;
		color: #fffbfa;
	}
	h3,
	h4 {
		color: #bfc0c0;
	}

	.footer,
	.navbar {
		background-color: #333;
		color: #fffbfa;
	}
	.huge-logo,
	.logo {
		filter: invert(1);
	}
	.nav-link {
		color: #fffbfa;
	}
	.nav-link.w--current {
		color: #bfc0c0;
		border-color: #bfc0c0;
	}
}

.logo {
	width: 50px;
	margin: 1rem;
	cursor: pointer;
}
</style>
