<template>
  <div v-if="visible" class="global-overlay" @click="handleClick">
    <div class="overlay-content" @click.stop>
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlobalOverlay',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    closable: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    handleClick() {
      if (this.closable) {
        this.$emit('close');
      }
    },
  },
};
</script>

<style scoped>
.global-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* Semi-transparent black */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.overlay-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

@media (min-width: 768px) {
  .overlay-content {
    max-width: 600px;
  }
}
</style>
