import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "pdap-design-system/styles";
import { FlexContainer } from "pdap-design-system";

const app = createApp(App);

app.use(router);

// Register 'FlexContainer' so it can be passed as a grid item
app.component("FlexContainer", FlexContainer);

app.mount("#app");
