<template>
    <div class="button-wrapper">
        <button v-on:click=''>
            <span class="white-text">{{name}}: {{active ? '\u2611' : '\u2610'}}</span>
        </button>
    </div>
</template>

<script>
export default {
    data(){
        return{
            //bool val
        }
    },

    props:{
        name:{
            type: String,
            required: true
        }
    },

    methods:{
        toggle: function(){
            this.active = !this.active
        },

        toggleAndEmit: function(){
            this.toggle()
            this.$emit('toggle', this.active)
        }
    }
}
</script>

<style scoped>
    .button-wrapper{
        display:flex;
        align-items: center;
    }
</style>
