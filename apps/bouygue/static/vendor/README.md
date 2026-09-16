# Third-party front-end libraries

Served from the site itself, so pages make no request to an outside CDN.
Each file is the unmodified upstream build, checked identical on two CDNs
(and, for jQuery, against its published SRI hash) when it was added.

| Library | Version | Upstream file | Licence |
|---|---|---|---|
| jQuery | 3.5.1 | https://code.jquery.com/jquery-3.5.1.min.js | MIT |
| Bootstrap (JS bundle, with Popper) | 4.5.3 | https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js | MIT |
| Font Awesome Free (SVG + JS) | 5.15.1 | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/js/all.min.js | Icons CC BY 4.0, code MIT |
| Feather icons | 4.24.1 | https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.24.1/feather.min.js | MIT |
| Chart.js | 2.9.4 | https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js | MIT |

The site's fonts live in `bouygue/assets/fonts/`; FullCalendar and the image
cropping widget ship with the project and its Python packages.
To update a library, replace the folder with the new version and change the
paths in the templates.
