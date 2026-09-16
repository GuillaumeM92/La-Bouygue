from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class StaticStorage(ManifestStaticFilesStorage):
    """Static files named after a hash of their content.

    collectstatic writes bergerie.3f2a1c9e7b10.css next to bergerie.css, and
    {% static %} points to the hashed name, so Nginx can let browsers keep
    these files for a year: a changed file gets a new name.

    A file missing from the manifest falls back to its plain name rather than
    breaking the page.
    """
    manifest_strict = False
