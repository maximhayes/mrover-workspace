<template>
  <div class='wrap'>
    <span v-bind:class='["led", color]'>
      </span>
    <span class='name'>{{name}}</span>
  </div>
</template>

<script>
export default {
  props: {
    connected: {
      type: Boolean,
      required: true
    },
    name: {
      type: String,
      required: true
    }
  },

  computed: {
    color: function () {
      return this.connected ? 'green' : 'red'
    }
  }
}
</script>

<style scoped>
  .wrap {
    display: flex;
    align-items: center;
    height: 100%;
  }

  .led {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 1px solid;
  }

  .green {
    background-color: lightgreen;
  }

  .red {
    background-color: red;
  }

  .name {
    margin-left: 5px;
  }
</style>
