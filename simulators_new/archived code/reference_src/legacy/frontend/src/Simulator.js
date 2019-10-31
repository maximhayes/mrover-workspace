import Vue from 'vue'
import Simulator from "./Simulator.vue"

Vue.config.productionTip = false;

new Vue({
    el: '#Simulator',
    components: { Simulator },
    template: '<Simulator/>'
})