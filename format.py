import sublime
import sublime_plugin
import subprocess
import os


def is_swift(view):
    return view.score_selector(0, 'source.swift') > 0


def settings():
    return sublime.load_settings('SwiftFormat.sublime-settings')


def save_settings():
    return sublime.save_settings('SwiftFormat.sublime-settings')


def swiftformat(args=[], input=None):
    binary = settings().get('swift_format_binary') or 'swiftformat'
    return subprocess.Popen(
        [binary] + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True).communicate(input=input)


def print_error(error):
    print('SwiftFormat:', error)


class SwiftFormatSelectionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                continue

            selection = self.view.substr(region)
            output, error = swiftformat(input=selection)
            if not error:
                self.view.replace(edit, region, output)
            else:
                print_error(error)


class SwiftFormatFileCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return is_swift(self.view)

    def run(self, edit):
        args = [self.view.file_name()]
        output, error = swiftformat(args)
        if error:
            print_error(error)


class SwiftFormatListener(sublime_plugin.EventListener):

    def on_post_save_async(self, view):
        if is_swift(view) and settings().get('swift_format_on_save'):
            view.run_command('swift_format_file')


class SwiftFormatToggleOnSaveCommand(sublime_plugin.ApplicationCommand):

    def is_checked(self):
        return settings().get('swift_format_on_save')

    def run(self):
        format_on_save = settings().get('swift_format_on_save')
        settings().set('swift_format_on_save', not format_on_save)
        save_settings()


class SwiftFormatEnableOnSaveCommand(SwiftFormatToggleOnSaveCommand):

    def is_visible(self):
        return not settings().get('swift_format_on_save')


class SwiftFormatDisableOnSaveCommand(SwiftFormatToggleOnSaveCommand):

    def is_visible(self):
        return settings().get('swift_format_on_save')
