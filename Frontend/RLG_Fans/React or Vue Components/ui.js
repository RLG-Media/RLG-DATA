// ui.js - Vuex module for managing UI state
export const state = () => ({
    isSidebarVisible: false,
    isGlobalOverlayVisible: false,
    isLoaderVisible: false,
  });
  
  export const mutations = {
    toggleSidebar(state) {
      state.isSidebarVisible = !state.isSidebarVisible;
    },
    setSidebarVisibility(state, visibility) {
      state.isSidebarVisible = visibility;
    },
    showGlobalOverlay(state) {
      state.isGlobalOverlayVisible = true;
    },
    hideGlobalOverlay(state) {
      state.isGlobalOverlayVisible = false;
    },
    toggleGlobalOverlay(state) {
      state.isGlobalOverlayVisible = !state.isGlobalOverlayVisible;
    },
    showLoader(state) {
      state.isLoaderVisible = true;
    },
    hideLoader(state) {
      state.isLoaderVisible = false;
    },
    toggleLoader(state) {
      state.isLoaderVisible = !state.isLoaderVisible;
    },
  };
  
  export const actions = {
    toggleSidebar({ commit }) {
      commit('toggleSidebar');
    },
    setSidebarVisibility({ commit }, visibility) {
      commit('setSidebarVisibility', visibility);
    },
    showGlobalOverlay({ commit }) {
      commit('showGlobalOverlay');
    },
    hideGlobalOverlay({ commit }) {
      commit('hideGlobalOverlay');
    },
    toggleGlobalOverlay({ commit }) {
      commit('toggleGlobalOverlay');
    },
    showLoader({ commit }) {
      commit('showLoader');
    },
    hideLoader({ commit }) {
      commit('hideLoader');
    },
    toggleLoader({ commit }) {
      commit('toggleLoader');
    },
  };
  
  export const getters = {
    isSidebarVisible: (state) => state.isSidebarVisible,
    isGlobalOverlayVisible: (state) => state.isGlobalOverlayVisible,
    isLoaderVisible: (state) => state.isLoaderVisible,
  };
  