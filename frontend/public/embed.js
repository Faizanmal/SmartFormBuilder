(function (window, document) {
  'use strict';

  var FormForge = {
    version: '1.1.0',
    config: {
      apiBaseUrl: 'https://api.formforge.io',
      embedBaseUrl: 'https://forms.formforge.io',
      debug: false
    }
  };

  // Debug logger
  function log() {
    if (FormForge.config.debug && console && console.log) {
      console.log.apply(console, ['[FormForge]'].concat(Array.prototype.slice.call(arguments)));
    }
  }

  function createIframe(src, attrs) {
    var iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.style.width = attrs.width || '100%';
    iframe.style.height = attrs.height || '600px';
    iframe.style.border = attrs.border || 'none';
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('scrolling', attrs.scrolling || 'no');
    iframe.setAttribute('allow', 'payment');
    iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups');
    iframe.style.borderRadius = attrs.borderRadius || '8px';
    iframe.style.display = 'block';
    iframe.className = attrs.className || 'formforge-embed-iframe';
    
    // Add loading attribute for performance
    if ('loading' in iframe) {
      iframe.loading = 'lazy';
    }
    
    return iframe;
  }

  function listenForHeight(iframe, origin, callbacks) {
    callbacks = callbacks || {};
    
    function onMessage(e) {
      // Validate origin for security
      if (origin && e.origin !== origin) {
        log('Message from untrusted origin:', e.origin);
        return;
      }
      
      try {
        var msg = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
        
        if (!msg || !msg.type) return;
        
        log('Received message:', msg.type, msg);
        
        // Handle height updates
        if (msg.type === 'formforge:height' && msg.height) {
          iframe.style.height = msg.height + 'px';
          if (callbacks.onResize) callbacks.onResize(msg.height);
        }
        
        // Handle submission success
        if (msg.type === 'formforge:submitted') {
          var ev = new CustomEvent('formforge:submitted', { detail: msg.payload || {} });
          iframe.dispatchEvent(ev);
          if (callbacks.onSubmit) callbacks.onSubmit(msg.payload);
        }
        
        // Handle errors
        if (msg.type === 'formforge:error') {
          log('Form error:', msg.error);
          if (callbacks.onError) callbacks.onError(msg.error);
        }
        
        // Handle ready state
        if (msg.type === 'formforge:ready') {
          log('Form ready');
          if (callbacks.onReady) callbacks.onReady();
        }
        
      } catch (err) {
        log('Error parsing message:', err);
      }
    }

    window.addEventListener('message', onMessage, false);

    return function cleanup() {
      window.removeEventListener('message', onMessage, false);
    };
  }

  // embed into a container selector
  FormForge.embed = function (opts) {
    // opts: { formId, slug, container, theme, width, height, onSubmit, onReady, onError, prefill, hideFields }
    if (!opts) {
      log('Error: No options provided to FormForge.embed');
      return null;
    }
    
    var slug = opts.slug || opts.formId;
    if (!slug) {
      log('Error: slug or formId is required');
      return null;
    }
    
    var container = typeof opts.container === 'string' ? document.querySelector(opts.container) : opts.container;
    if (!container) {
      log('Error: container not found');
      if (opts.onError) opts.onError('Container not found');
      return null;
    }

    var baseUrl = opts.embedBaseUrl || FormForge.config.embedBaseUrl;
    var src = opts.src || (baseUrl + '/form/' + slug);
    
    // Build query parameters
    var params = [];
    if (opts.theme) params.push('theme=' + encodeURIComponent(opts.theme));
    if (opts.prefill) params.push('prefill=' + encodeURIComponent(JSON.stringify(opts.prefill)));
    if (opts.hideFields) params.push('hide=' + encodeURIComponent(opts.hideFields.join(',')));
    if (opts.transparent) params.push('transparent=1');
    
    if (params.length > 0) {
      src = src + (src.indexOf('?') === -1 ? '?' : '&') + params.join('&');
    }

    var iframeAttrs = {
      width: opts.width || '100%',
      height: opts.height || '600px',
      borderRadius: opts.borderRadius || '8px',
      scrolling: opts.scrolling || 'no',
      className: opts.className || 'formforge-embed-iframe'
    };
    
    var iframe = createIframe(src, iframeAttrs);
    
    // Show loading state
    if (opts.showLoader !== false) {
      var loader = document.createElement('div');
      loader.className = 'formforge-loader';
      loader.style.textAlign = 'center';
      loader.style.padding = '40px';
      loader.innerHTML = opts.loaderHtml || 'Loading form...';
      container.appendChild(loader);
    }

    // Clear container and append iframe
    setTimeout(function() {
      container.innerHTML = '';
      container.appendChild(iframe);
    }, opts.loaderDelay || 100);

    var callbacks = {
      onSubmit: opts.onSubmit,
      onReady: opts.onReady,
      onError: opts.onError,
      onResize: opts.onResize
    };

    var cleanup = listenForHeight(iframe, baseUrl, callbacks);

    // Attach custom submit event listener
    if (typeof opts.onSubmit === 'function') {
      iframe.addEventListener('formforge:submitted', function (ev) {
        try {
          opts.onSubmit(ev.detail);
        } catch (err) {
          log('Error in onSubmit callback:', err);
        }
      });
    }

    // Return API for consumer
    return {
      iframe: iframe,
      container: container,
      destroy: function () {
        cleanup();
        if (iframe && iframe.parentNode) {
          iframe.parentNode.removeChild(iframe);
        }
      },
      reload: function() {
        iframe.src = iframe.src;
      },
      prefill: function(data) {
        iframe.contentWindow.postMessage(JSON.stringify({
          type: 'formforge:prefill',
          data: data
        }), baseUrl);
      }
    };
  };

  // popup (modal) implementation
  FormForge.popup = function (opts) {
    // opts: { formId, slug, width, height, theme }
    opts = opts || {};
    var slug = opts.slug || opts.formId;
    var src = (opts.src || (window.location.origin + '/form/' + slug));
    if (opts.theme) src = src + (src.indexOf('?') === -1 ? '?' : '&') + 'theme=' + encodeURIComponent(opts.theme);

    // overlay
    var overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.left = 0;
    overlay.style.top = 0;
    overlay.style.right = 0;
    overlay.style.bottom = 0;
    overlay.style.background = 'rgba(0,0,0,0.5)';
    overlay.style.zIndex = 999999;
    overlay.className = 'formforge-overlay';

    // container
    var wrapper = document.createElement('div');
    wrapper.style.position = 'absolute';
    wrapper.style.left = '50%';
    wrapper.style.top = '50%';
    wrapper.style.transform = 'translate(-50%, -50%)';
    wrapper.style.width = (opts.width ? opts.width + 'px' : '600px');
    wrapper.style.height = (opts.height ? opts.height + 'px' : '700px');
    wrapper.style.background = '#fff';
    wrapper.style.borderRadius = '8px';
    wrapper.style.overflow = 'hidden';
    wrapper.style.boxShadow = '0 10px 40px rgba(0,0,0,0.25)';
    wrapper.className = 'formforge-popup-wrapper';

    var closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.style.position = 'absolute';
    closeBtn.style.right = '8px';
    closeBtn.style.top = '8px';
    closeBtn.style.zIndex = 1000000;
    closeBtn.style.background = 'transparent';
    closeBtn.style.border = 'none';
    closeBtn.style.fontSize = '24px';
    closeBtn.style.cursor = 'pointer';

    var iframe = createIframe(src, { width: '100%', height: '100%', borderRadius: 0 });

    wrapper.appendChild(closeBtn);
    wrapper.appendChild(iframe);
    overlay.appendChild(wrapper);
    document.body.appendChild(overlay);

    var cleanup = listenForHeight(iframe, window.location.origin);

    function destroy() {
      cleanup();
      try { document.body.removeChild(overlay); } catch (e) {}
    }

    closeBtn.addEventListener('click', destroy);

    // close on overlay click
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) destroy();
    });

    return { iframe: iframe, destroy: destroy };
  };

  // helper: open hosted form in a new window
  FormForge.open = function (opts) {
    opts = opts || {};
    var slug = opts.slug || opts.formId;
    var url = opts.src || (window.location.origin + '/form/' + slug);
    var w = opts.width || 900;
    var h = opts.height || 700;
    var left = (screen.width / 2) - (w / 2);
    var top = (screen.height / 2) - (h / 2);
    window.open(url, 'FormForge', 'toolbar=0,location=0,menubar=0,width=' + w + ',height=' + h + ',top=' + top + ',left=' + left + ',resizable=1');
  };

  // expose
  window.FormForge = FormForge;

  // postMessage instructions for embedded forms:
  // From the embedded form, send: window.parent.postMessage(JSON.stringify({ type: 'formforge:height', height: 1200 }), '*');
  // On submission send: window.parent.postMessage(JSON.stringify({ type: 'formforge:submitted', payload: { id: 'abc', values: {...} } }), '*');

})(window, document);
