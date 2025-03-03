# PDAP Design System
_A `Vue` component library, styling system, and image asset repository for PDAP-branded client apps._

[![Current npm release](https://img.shields.io/npm/v/pdap-design-system?style=for-the-badge)](https://www.npmjs.com/package/pdap-design-system)
![Build status](./badges/build.svg) 
![Test coverage](./badges/coverage.svg) 
![License](https://img.shields.io/github/license/Police-Data-Accessibility-Project/design-system.svg?style=for-the-badge&color=green) 


[![Discord](https://img.shields.io/discord/828274060034965575?logo=discord&style=for-the-badge&color=blue)](https://discord.gg/vKhDv7nC8B)


## Usage

1. Install the package

```
npm install pdap-design-system
```

2. Import the stylesheet in the app's entrypoint (usually `index.js` or `main.js`, at the root of your project)

```
// index.js | main.js

import 'pdap-design-system/styles';
```

3. Import and use the components

```
import { Button, Form } from 'pdap-design-system';
```

1. Extend the `es-lint` config, for consistency in linting between client apps:
First `npm install --save-dev @pdap-design-system/eslint-config`, then, in `eslintrc`:

```
{ 
  ...,
	extends: [
		"@pdap-design-system/eslint-config",
    ...
	],
}
```


5. (Optional) Import the tailwind config if you need to use additional tailwind styles.

```
// tailwind.config.js
import { tailwindConfig } from 'pdap-design-system';

/** @type {import('tailwindcss').Config} */
module.exports = {
  // Spread base config
  ...tailwindConfig,
  // Then override with `content` property and any other superseding config (if necessary - it really shouldn't be)
  content: [
    "./index.html",
    "./src/**/*.{vue,js,css}",
  ],
}

```

6. If the project is using `TypeScript`, the component props definitions and other types are exposed for import as well.  
   _n.b. This can be particularly useful for composing `Form` schemas, where `Input` schema objects are defined differently depending on the `type` of input desired._

```
import { PdapInputTypes } from 'pdap-design-system';
```

6. See [the component documentation](./docs/components.md) for details on each component's API.

### About images

PDAP image assets contained in this repo are built to the `/dist` directory. For convenience an importing alias `/images` has been added.

```
import 'pdap-design-system/images/acronym.svg';
```

Or, if you need them all, you can import all images at the app level. Just remember that if it's imported it gets bundled with your production app, so take care not to import unneeded images.

```
import `pdap-design-system/images`;
```

### Using the CLI to copy assets to your local project directory

If you want either styles or images copied to a local directory, you can do so from the root directory of your project.

Assets can be copied using the `pdap-design-system` command line method exposed by this package.

One of the following arguments is required:  
`--copy-assets`: Copies all images and styles.
`--copy-images`: Copies all images.
`--copy-styles`: Copies all styles.

The following argument is optional:  
`--to={path}`: Path to directory where assets should be copied. Defaults to `assets`

```
  pdap-design-system --copy-images --to=image-assets
```

## Development Setup

1. Clone the repo

```
gh repo clone Police-Data-Accessibility-Project/design-system
```

2. CD into the project directory and install dependencies

```
cd design-system
npm i
```

3. Step 2 should result in the `build` script being run after packages are installed. Check the `dist` directory for changes. You then may want to take one or both of the following steps:

- If `build` wasn't called when you installed deps, build styles and images to the `dist` directory:

```
npm run build
```

- To watch for changes and update the build as you make changes:

```
npm run build:watch
```

4. If you use VS Code as your editor, you may want to install the [tailwind VS Code extension](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss), which helps with intellisense and the custom at-rules used by TailwindCSS.

5. Read the [contributing guide](./CONTRIBUTING.md) for development requirements and tips.

## Assets

Use these [brand assets](https://docs.pdap.io/meta/about/staff/brand-assets).
Use this [terminology](https://docs.pdap.io/activities/terms-and-definitions).

## Scripts reference

| Script         | What it does                                             |
| -------------- | -------------------------------------------------------- |
| `_commit`      | Create conventional commits                              |
| `build`        | Builds the library                                       |
| `build:watch`  | Builds the library and watches for file changes          |
| `ci`           | Remove all generated files and re-installs deps         |
| `clean`        | Remove all generated files (except `package-lock.json`) |
| `clean:deps`   | Remove node_modules directory                           |
| `clean:build`  | Remove dist directory                                   |
| `clean:test`   | Remove testing coverage reports                         |
| `lint`         | Lint everything                                         |
| `lint:es`      | Lint `ts`  and `vue` with `eslint`                       |
| `lint:css`     | Lint `css` and `vue` with `stylelint`                    |
| `lint:ts`      | Lint `ts` with `tsc`                                     |
| `test`         | Run all test suites                                     |
| `test:changed` | Run only test suites affected by changed files          |
| `typecheck`    | Run type check on all `ts` and `vue` files              |


_n.b. There are some other scripts defined in the `package.json` `"scripts"` field, but they are mostly for CI or cleanup post-build, etc. You shouldn't need them._
