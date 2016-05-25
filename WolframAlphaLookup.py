import sublime, sublime_plugin, requests

from xml.etree import ElementTree as ET

class WolframAlphaLookupCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.set_timeout_async(self.run_async, 1)

    def run_async(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.has("wolfram_api_key"):
            API_KEY = settings.get("wolfram_api_key")
            queries = []
            for region in self.window.active_view().sel():
                if not region.empty():
                    query = self.window.active_view().substr(region)
                else:
                    query = self.window.active_view().substr(self.window.active_view().line(region))
                queries.append(query.strip())

            if queries:
                r = requests.get("http://api.wolframalpha.com/v2/query", params={
                    "input": " ".join(queries),
                    "appid": API_KEY
                })

                root = ET.fromstring(r.text)
                if root.get('success') == 'true':
                    items = list()
                    for pod in root.iter('pod'):
                        title = pod.attrib.get('title')
                        plaintext = pod.find('./subpod/plaintext').text
                        if title and plaintext:
                            items.append([plaintext, title])

                    def on_select(index):
                        if index > -1:
                            sublime.set_clipboard(items[index][0])

                    self.window.show_quick_panel(items, on_select)
                else:
                    print(r.text)
                    sublime.error_message("Wolfram|Alpha could not understand your query!")
        else:
            sublime.error_message("Please add a \"wolfram_api_key\" to the settings!")
