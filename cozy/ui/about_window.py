from collections import defaultdict

from gi.repository import Adw, Gio, Gtk


class AboutWindow:
    def __init__(self, version: str) -> None:
        self._window = Adw.AboutWindow.new_from_appdata(
            "/com/github/geigi/cozy/appdata/com.github.geigi.cozy.appdata.xml",
            release_notes_version=version,
        )

        contributors = self.get_contributors()
        self._window.set_developers(sorted(contributors["code"]))
        self._window.set_designers(sorted(contributors["design"]))
        self._window.set_artists(sorted(contributors["icon"]))

        self._window.set_license_type(Gtk.License.GPL_3_0)

        # Translators: Replace "translator-credits" with your names, one name per line
        self._window.set_translator_credits(_("translator-credits"))

        self.set_extra_credits()

    def get_contributors(self) -> list[str]:
        authors_file = Gio.resources_lookup_data(
            "/com/github/geigi/cozy/appdata/authors.list", Gio.ResourceLookupFlags.NONE
        )

        current_section = ""
        result = defaultdict(list)
        for line in authors_file.get_data().decode().splitlines():
            if line.startswith("#"):
                current_section = line[1:].strip().lower()
            elif line.startswith("-"):
                result[current_section].append(line[1:].strip())

        return result

    def set_extra_credits(self) -> None:
        self._window.add_acknowledgement_section(
            _("Patreon Supporters"),
            ["Fred Warren", "Gabriel", "Hu Mann", "Josiah", "Oleksii Kriukov"],
        )
        self._window.add_acknowledgement_section(_("m4b chapter support in mutagen"), ("mweinelt",))
        self._window.add_acknowledgement_section(
            _("Open Source Projects"),
            ("Lollypop music player https://gitlab.gnome.org/World/lollypop",),
        )

        self._window.add_legal_section(
            "python-inject", "© 2010 Ivan Korobkov", Gtk.License.APACHE_2_0
        )

    def present(self, parent: Adw.ApplicationWindow) -> None:
        self._window.set_transient_for(parent)
        self._window.present()
