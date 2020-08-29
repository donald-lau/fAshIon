import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import './registerServiceWorker'
import Argon from "./plugins/argon-kit";
// import  {VBTooltip} from 'bootstrap-vue';
import BootstrapVue from 'bootstrap-vue'
import VueSingleSelect from "vue-single-select";
Vue.config.productionTip = false;


Vue.use(Argon);
// Vue.directive('b-tooltip', VBTooltip);
Vue.use(BootstrapVue);
Vue.component('vue-single-select', VueSingleSelect);
new Vue({
  router,
  render: h => h(App)
}).$mount("#app");
