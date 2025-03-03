# PDAP Component Documentation

Documentation for PDAP component usage

## Table of Contents

- [Button](#button)
  - [Props](#props)
  - [Example](#example)
- [FlexContainer](#flexcontainer)
  - [Props](#props-1)
  - [Example](#example-1)
- [Footer](#footer)
  - [Props](#props-2)
  - [Example](#example-2)
- [Form](#form)
  - [Props](#props-3)
  - [Example](#example-3)
- [GridContainer](#gridcontainer)
  - [Props](#props-4)
  - [Example](#example-4)
- [GridItem](#griditem)
  - [Props](#props-5)
  - [Example](#example-5)
- [Header](#header)
  - [Props](#props-6)
  - [Example](#example-6)
- [Input](#input)
- [Nav](#nav)
  - [Example](#example-7)
- [QuickSearchForm](#quicksearchform)
  - [Props](#props-7)
- [TileIcon](#tileicon)
  - [Props](#props-8)
  - [Example](#example-8)

## Button

### _Props_

| name        | required? | types                    | description                | default   |
| ----------- | --------- | ------------------------ | -------------------------- | --------- |
| `isLoading` | no        | `boolean`                | Request state              | `false`   |
| `intent`    | yes       | `primary` \| `secondary` | Determines style of button | `primary` |

### _Example_

```
<template>
  <Button class="custom-btn-class" intent="primary" @click="() => console.log('hello world')" type="button">Click me</Button>
</template>

...

<script>
import { Button } from 'pdap-design-system';

...

export default {
  components: ['Button'],
  ...
}
</script>

...

<style>
.custom-btn-class {
  padding: 12px;
}
</style>
```

## FlexContainer

All container components are designed to be dynamic and take any `HTMLElement` tag as the component to be rendered. `FlexContainer` can itself be passed as the element type for `GridItem`, for example, or vice versa, allowing us to easily compose complex layouts (more on this later with the `GridContainer` and `GridItem` documentation).

### _Props_

| name        | required? | types               | description                         | default |
| ----------- | --------- | ------------------- | ----------------------------------- | ------- |
| `component` | no        | `string`            | HTML Element to render as container | `'div'` |
| `alignment` | no        | `start` \| `center` | Flex alignment presets              | `start` |

### _Example_

```
<template>
	<FlexContainer alignment="center" component="card">
      <h2>Some content goes here</h2>
      <p>More content goes here.</p>
      <Button class="custom-button-class-name" :isLoading="isLoading" @click="() => console.log('hello world')">
        Say hello with this button
      </Button>
	</FlexContainer>
</template>

...

<script>
import { Button, FlexContainer } from 'pdap-design-system';

...

export default {
  components: ['Button', 'FlexContainer'],
  props: ['requestPending', ...],
  data() {
    return {
      isLoading: this.requestPending
    }
  }
  ...
}
</script>
```

## Footer

### _Props_

| name                  | required? | types    | description            | default                                                     |
| --------------------- | --------- | -------- | ---------------------- | ----------------------------------------------------------- |
| `logoImageSrc`        | no        | `string` | Source of logo image   | `'node_modules/pdap-design-system/dist/images/acronym.svg'` |
| `logoImageAnchorPath` | no        | `string` | Flex alignment presets | `/`                                                         |

### _Notes_

The `Footer` component provides support for overriding the default social links. The `links` variable is `inject`ed by the component, using the following defaults:

```
export default {
  ...
  inject: {
    footerLinks: {
      default: [
	      {
	      	to: 'https://github.com/orgs/Police-Data-Accessibility-Project',
	      	text: 'Github',
	      },
	      {
	      	to: 'ttps://discord.gg/wMqex8nKZJ',
	      	text: 'Discord',
	      },
	      {
	      	to: 'https://www.linkedin.com/company/pdap',
	      	text: 'LinkedIn',
	      },
      ]
    }
  },
  data() {
    return {
      links: this.footerLinks;
    }
  }
}
```

If we desire different links somewhere that `Footer` is rendered, simply `provide` an overriding array from a parent component, like so:

### _Example_

```
<template>
  <Header />
  <router-view />
  <Footer />
</template>

...

<script>
import { Header, Footer } from 'pdap-design-system';
import { RouterView } from 'vue-router'

...

export default {
  name: 'Layout',
  components: ['Header', 'Footer'],
  ...
  provide: {
    navLinks: [...]
  }
}
</script>

```

## Form

The `Form` component is powerful. All you need to do is pass a few props, and the component will generate inputs and render them in the UI, complete with customizable form validation and both form-level and input-level error states.

### _Props_

| name     | required? | types                             | description                        | default     |
| -------- | --------- | --------------------------------- | ---------------------------------- | ----------- |
| `error`  | no        | `string` \| `undefined` \| `null` | Error state                        | `undefined` |
| `id`     | yes       | `string`                          | Form id                            | none        |
| `name`   | yes       | `string`                          | Form name                          | none        |
| `schema` | yes       | `PdapFormSchema`                  | Array of schema entries for inputs | none        |

### _Notes_

- Form schema entries can look different depending on the type of input. We currently only use text inputs, so the example only displays these.
- To properly submit the form, you must render a button with `type="submit"` _inside_ of the `Form` component.
- `Form` emits a `submit` event and passes all values to the handler you pass to `on-submit`
- Currently available form validations are defined by the `PdapFormValidators` interface:

```

PdapFormValidators {
  maxLength: {
    message?: string;
    value: number;
  };
  minLength: {
    message?: string;
    value: number;
  };
  required: {
    message?: string;
    value: boolean;
  };
}

```

- The `message` property is optional. If it is not passed, Vuelidate will default to a generic error message. The `value` property is the value you want to validate against. (i.e. for a required field with a max length of 12 characters, we might pass:

```
// For a custom message
{
  ...,
  validators: {
    maxLength: {
      message: 'No more than twelve characters, please!',
      value: 12
    },
    required: {
      message: 'Pretty please enter this field.',
      value: true
    }
  }
}

// For the default Vuelidate message
{
  ...,
  validators: {
    maxLength: {
      value: 12
    },
    required: {
      value: true
    }
  }
}


```

)

### _Example_

```

<template>
  <Form :schema="formSchema" :on-submit="handleSubmit" id="test-form" name="data-request-form">
    <Button intent="primary" type="submit">Click me</Button>
  </Form>
</template>

...

<script>
import { Button, Form, PdapInputTypes } from 'pdap-design-system';

...

export default {
  components: ['Button', 'Form'],
  data() {
    return {
      formSchema: [
        {
          id: 'testfirstname',
          name: 'firstName',
          label: 'First Name',
          type: 'text',
          placeholder: 'John',
          value: '',
          validators: {
            minLength: {
              value: 3
            },
            required: {
              message: 'Please provide this information',
              value: true
            }
          },
        },
        {
          id: 'testlastname',
          name: 'lastName',
          label: 'Last Name',
          type: 'text',
          placeholder: 'Doe',
          value: '',
          validators: {
            minLength: {
              value: 3
            },
            maxLength: {
              message: 'A thousand characters for your surname? Are you a bot?',
              value: 999
            },
          },
        }
      ]
    }
  },
  methods: {
    handleSubmit: async function(data) {
      await doRequestStuff(data);
      this.$router.push('/')
    }
  }
  ...
}
</script>

```

## GridContainer

All container components are designed to be dynamic and take any `HTMLElement` tag as the component to be rendered. It also works with the `GridItem` component (see example below). `GridContainer` and `GridItem` could both be passed as the element type for `FlexContainer`, for example, or vice versa, allowing us to easily compose complex layouts.

### _Props_

| name              | required? | types                         | description                                         | default             |
| ----------------- | --------- | ----------------------------- | --------------------------------------------------- | ------------------- |
| `columns`         | no        | `1` \| `2` \| `3` \| `'auto'` | Number of grid columns                              | `'auto'`            |
| `component`       | no        | `string`                      | HTML Element to render as container                 | `'div'`             |
| `rows`            | no        | `number` \| `'auto'`          | Number of grid rows                                 | `'auto'`            |
| `templateColumns` | no        | `string` \| `undefined`       | Custom `grid-template-columns` value, passed inline | `undefined` (no-op) |
| `templateRows`    | no        | `string` \| `undefined`       | Custom `grid-template-rows` value, passed inline    | `undefined` (no-op) |

### _Notes_

- Grid layouts max out at 3 columns, and responsiveness is baked in.
  - i.e. When you render a 3-column grid layout, it automatically resizes to 2 columns, then 1 column, as screen widths decrease.
  - In this case, it is a best practice to leave the `rows` prop as its default `'auto'` value, to ensure that the layout fills as many rows as are needed when the number of columns decreases

### _Example_

```
<template>
  <GridContainer :columns="3" component="section">
    <GridItem component="FlexContainer">
      <h2>Some content goes here</h2>
      <p>More content goes here.</p>
      <Button class="custom-button-class-name" :isLoading="isLoading" @click="() => console.log('hello world')">
        Say hello with this button
      </Button>
    </GridItem>
  </GridContainer>
</template>

...

<script>
import { Button, FlexContainer } from 'pdap-design-system';

...

export default {
  components: ['Button', 'FlexContainer', 'GridContainer', 'GridItem'],
  props: ['requestPending', ...],
  data() {
    return {
      isLoading: this.requestPending
    }
  },
  ...
}
</script>
```

## GridItem

### _Props_

| name         | required? | types             | description                         | default |
| ------------ | --------- | ----------------- | ----------------------------------- | ------- |
| `component`  | no        | `string`          | HTML Element to render as grid item | `'div'` |
| `spanColumn` | no        | `1` \| `2` \| `3` | Columns grid item should span       | `1`     |
| `spanRow`    | no        | `number`          | Rows grid item should span          | `1`     |

### _Notes_

- Grid layouts max out at 3 columns, and responsiveness is baked in.
  - i.e. When you render a 3-column grid layout, it automatically resizes to 2 columns, then 1 column, as screen widths decrease.
  - In this case, it is a best practice to leave the `rows` prop as its default `'auto'` value, to ensure that the layout fills as many rows as are needed when the number of columns decreases

### _Example_

See `GridContainer` above.

## Header

### _Props_

| name                  | required? | types    | description            | default                                                    |
| --------------------- | --------- | -------- | ---------------------- | ---------------------------------------------------------- |
| `logoImageSrc`        | no        | `string` | Source of logo image   | `'node_modules/pdap-design-system/dist/images/lockup.svg'` |
| `logoImageAnchorPath` | no        | `string` | Flex alignment presets | `/`                                                        |

### _Notes_

The `Header` component does not require any props to be passed. But keep in mind that it is responsible for rendering the `Nav` component. Consuming applications will need to `provide` an array of nav links — **there are no defaults for this**, you must `provide` these links either 1. in a layout component (see example below), at the route level, or at the app level. This allows for flexibility in which links are rendered on which routes

### _Example_

```
<template>
  <Header />
  <router-view />
  <Footer />
</template>

...

<script>
import { Header, Footer } from 'pdap-design-system';
import { RouterView } from 'vue-router'

...

export default {
  name: 'Layout',
  components: ['Header', 'Footer'],
  ...
  provide: {
    navLinks: [...]
  }
}
</script>

```

## Input

Inputs are rendered by the `Form` component via a schema. Please see `Form` for more details

## Nav

You do not need to render `Nav` directly. `Header` takes care of that. But you do need to `provide` nav link data from a parent component. This allows for nav links to be dynamic depending on where `Header` is rendered.

### _Example_

```

<template>
  <Header />
  <router-view />
  <Footer />
</template>

...

<script>
import { Footer, Header } from 'pdap-design-system';
import { RouterView } from 'vue-router';

...

export default {
  name: 'Layout',
  components: ['Footer', 'Header'],
  provide: {
    navLinks: [
      { path: '/', text: 'Home', method: 'path' },
      { path: '/a', text: 'a', method: 'path' },
      { path: '/b', text: 'b', method: 'path' },
      { path: '/c', text: 'c', method: 'path' },
      { href: 'https://www.google.com', text: 'Go to Google', method: 'href' },
    ]
  }
  ...

```

## QuickSearchForm

### _Props_

| name   | required? | types             | description                                                                | default  |
| ------ | --------- | ----------------- | -------------------------------------------------------------------------- | -------- |
| `mode` | no        | `'dev' \| 'prod'` | env. controls which url users are sent to when form is rendered on pdap.io | `'prod'` |

### _Notes_

The different `mode` prop values result the following base url values in the eventual navigation
| value | base url |
|--|--|
| `'dev'` | `'https://data-sources.pdap.dev'` |
| `'prod'` | `'https://data-sources.pdap.io'` |

## TileIcon

### _Props_

| name         | required? | types    | description                   | default |
| ------------ | --------- | -------- | ----------------------------- | ------- |
| `imgAltText` | yes       | `string` | Descriptive alt text for icon | none    |
| `imgSrc`     | yes       | `string` | Source of icon to render      | none    |

### _Example_

```

<template>
  <GridContainer :columns="3" component="section">
    <GridItem>
      <TileIcon :imgAltText="altText" :imgSrc="imagePath" >
    </GridItem>
  </GridContainer>
</template>

...

<script>
import { Header, Footer } from 'pdap-design-system';
import { RouterView } from 'vue-router'

...

export default {
  name: 'Layout',
  components: ['GridContainer', 'GridItem', 'TileIcon'],
  props: ['alt', 'src'],
  data() {
    return {
      altText: this.alt,
      imgSrc: this.src
    }
  }
}
</script>

```
