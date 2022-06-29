"use strict";

ckan.module('yasgui', function ($) {
  return {
    initialize: function($) {
      const endpoint = this.options.endpoint;
      const yasgui = new Yasgui(this.el[0], {
        requestConfig: { endpoint },
        copyEndpointOnNewTab: false,
      });
    }
  }
});

