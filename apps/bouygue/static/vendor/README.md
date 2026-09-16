# Third-party front-end libraries

Served from the site itself, so pages make no request to an outside CDN.
Each file is the unmodified upstream build, checked identical on two CDNs
and against its published SRI hash when it was added. Keep a library's
source map next to it when its last line names one: collectstatic fails
otherwise.

| Library | Version | Upstream file | Licence |
|---|---|---|---|
| jQuery | 3.7.1 | https://code.jquery.com/jquery-3.7.1.min.js | MIT |
| Bootstrap (JS bundle, with Popper, and its source map) | 4.6.2 | https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js | MIT |
| Font Awesome Free (SVG + JS) | 5.15.1 | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/js/all.min.js | Icons CC BY 4.0, code MIT |

The site's fonts live in `bouygue/assets/fonts/`; FullCalendar (5.5.1) and the image
cropping widget ship with the project and its Python packages.
Not upgraded on purpose (2026-09): FullCalendar 5.5.1 has no known
vulnerability, and a newer major would mean rewriting the calendar. Bootstrap 4 is end of life; CVE-2024-6531 (carousel)
has no 4.x fix but needs an attacker-controlled link, which the home page
carousel does not have.
To update a library, replace the folder with the new version and change the
paths in the templates.
