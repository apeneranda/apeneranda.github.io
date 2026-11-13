// Vidéo de l'accueil : la vignette est remplacée par le lecteur YouTube au clic.
// Rien n'est chargé depuis YouTube avant ; sans JavaScript, le lien ouvre YouTube.
(function () {
  document.querySelectorAll('a.video-frame[data-embed]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      var frame = document.createElement('div');
      frame.className = 'video-frame';
      var player = document.createElement('iframe');
      player.src = link.dataset.embed;
      player.title = link.dataset.title;
      player.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      player.allowFullscreen = true;
      player.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.appendChild(player);
      link.replaceWith(frame);
      player.focus();
    });
  });
})();
