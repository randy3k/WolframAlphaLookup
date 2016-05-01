import sublime, sublime_plugin, requests

from xml.etree import ElementTree as ET

class WolframCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings("Preferences.sublime-settings") 
        if settings.has("wolfram_api_key"):
            API_KEY = settings.get("wolfram_api_key")
            for region in self.window.active_view().sel():
                if not region.empty():
                    query = self.window.active_view().substr(region)
                else:
                    query = self.window.active_view().substr(self.window.active_view().line(region))
                query = query.strip()

                r = requests.get("http://api.wolframalpha.com/v2/query", params={
                    "input": query,
                    "appid": API_KEY
                })
                
                root = ET.fromstring(r.text)
                if root.get('success') == 'true':
                    items = list()
                    for pod in root.iter('pod'):
                        title = pod.attrib.get('title')
                        plaintext = pod.find('./subpod/plaintext').text
                        if title and plaintext:
                            items.append([title, plaintext])
                    
                    def on_select(index):
                        if index > -1:
                            print(items[index])
                            print(region)
                            self.window.active_view().run_command("insert_result", {"data": items[index][1]})

                    self.window.show_quick_panel(items, on_select)
                else:
                    sublime.error_message("Wolfram|Alpha could not understand your query!")
                break
        else:
            sublime.error_message("Please add a \"wolfram_api_key\" to the settings!")

class InsertResultCommand(sublime_plugin.TextCommand):
    def run(self, edit, data):
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                self.view.insert(edit, line.end(), '\n' + (data[:-1] if data[-1] == '\n' else data))
            else:
                self.view.insert(edit, region.end(), data)
            break
