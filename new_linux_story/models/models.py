import os
from new_linux_story.common import command_not_found


class CommandMissingDoFunction(Exception):
    pass


class CommandMissingAutocompleteFunction(Exception):
    pass


class CmdList(object):
    def __init__(self):
        # Merge these into one data structure?
        self._commands = {}

    def add_command(self, command_str, cls):
        self._commands[command_str] = cls

        # Check this has a "do" method, otherwise raise an exception
        # Possibly also check it has an autocomplete option, otherwise have
        # a default option of returning empty.
        do = getattr(cls, "do")
        autocomplete = getattr(cls, "autocomplete")
        if not (do and callable(do)):
            raise CommandMissingDoFunction
        elif not (autocomplete and callable(autocomplete)):
            raise CommandMissingAutocompleteFunction

    def receive_command(self, line):
        '''
        Take the line from the terminal and return the output the terminal
        would show.
        '''
        [command, string] = self._parse_input(line)
        if command in self._commands:
            return self._commands[command].do(string)
        else:
            return {"message": command_not_found, "files": []}

    def tab_once(self, line):
        '''
        If autocomplete returns a string, then there was only one option.
        If autocomplete returns an array, then there are many options.
        '''
        [command, string] = self._parse_input(line)
        if command in self._commands:
            return self._commands[command].tab_once(string)
        else:
            return ""

    def tab_many(self, line):
        '''
        If autocomplete returns a string, then there was only one option.
        If autocomplete returns an array, then there are many options.
        '''
        [command, string] = self._parse_input(line)
        if command in self._commands:
            return self._commands[command].tab_many(string)
        else:
            return ""

    def autocomplete(self, line):
        [command, string] = self._parse_input(line)
        if command in self._commands:
            return self._commands[command].autocomplete(string)
        else:
            return []

    def _parse_input(self, line):
        '''
        Returns the command word and the rest of the line.
        '''
        words = line.split(" ")
        parsed_input = [words[0], line.replace(words[0], "").strip()]
        return parsed_input


class CmdSingle(object):

    def __init__(self, user=None):
        # This is initialised elsewhere
        self._user = user

    @property
    def filesystem(self):
        return self._user.filesystem

    @property
    def position(self):
        return self._user.position

    def set_position(self, position):
        return self._user.set_position(position)

    def do(self):
        pass

    def autocomplete(self, line):
        return []


# This is not
class Echo(CmdSingle):

    def do(self, line):
        return line


class Pwd(CmdSingle):

    def do(self, line):
        return self.position


class Ls(CmdSingle):

    def __init__(self, user):
        self._rv = {
            "files": [],
            "message": ""
        }
        return super(Ls, self).__init__(user)

    def do(self, line):
        '''
        Returns a dictionary of the form
        {"files": [], "directories": [], "message": ""}
        '''
        if not line:
            return self._no_args()
        return self._no_flags(line)

    def _no_such_file_message(self, line):
        self._rv["message"] = (
            "ls: {}: No such file or directory".format(line)
        )
        return self._rv

    def _show_ls_at_position(self, position):
        self._rv["files"] = self.filesystem.get_all_at_path(position)
        return self._rv

    def _no_args(self):
        return self._show_ls_at_position(self.position)

    def _no_flags(self, line):
        path = os.path.join(self.position, line)
        (exists, f) = self.filesystem.path_exists(path)
        if not exists:
            return self._no_such_file_message(line)

        if not f.has_read_permission(self._user.name):
            self._rv["message"] = "ls: {}: Permission denied".format(line)
            return self._rv

        if f.type == "file":
            self._rv["message"] = line
            return self._rv
        elif f.type == "directory":
            self._rv["files"] = f.children
            return self._rv

    def autocomplete(self, line):
        return autocomplete(line, self.position, self.filesystem, "all")


class Cd(CmdSingle):

    def do(self, line):
        if not line:
            return self._no_args()

        return self._no_flags(line)

    def _no_such_file_message(self, name):
        return "cd: no such file or directory: {}".format(name)

    def _cd_into_file(self, name):
        return "bash: cd: {}: Not a directory".format(name)

    def _no_args(self):
        self.set_position("~")

    def _no_flags(self, line):
        path = os.path.normpath(os.path.join(self.position, line))
        (exists, f) = self.filesystem.path_exists(path)
        if not exists:
            return self._no_such_file_message(line)
        elif not f.type == "directory":
            return self._cd_into_file(line)
        elif not f.has_execute_permission(self._user.name):
            return "cd: permission denied: {}".format(line)
        else:
            self._user.set_position(path)

    def autocomplete(self, line):
        # needed for Cmd module, which handles the tab_once/tab_many
        # condition
        return autocomplete(line, self.position, self.filesystem, "dirs")


class Cat(CmdSingle):

    def do(self, line):
        if not line:
            self._no_arguments()
            return

        return self._no_flags(line)

    def _no_arguments(self):
        '''
        cat without arguments just echos out what the user last
        typed. Change this behaviour and pass message to the user.
        '''
        return ("Use the format \"cat filepath\" for a filepath of "
                "your choice.")

    def _no_such_file_message(self, name):
        return "cat: {}:no such file or directory".format(name)

    def _no_flags(self, line):
        path = os.path.join(self.position, line)

        (exists, f) = self.filesystem.path_exists(path)
        if not exists:
            return self._no_such_file_message(line)
        elif not f.has_read_permission(self._user.name):
            return "cat: {}: Permission denied".format(line)
        else:
            return f.content

    def autocomplete(self, line):
        # needed for Cmd module, which handles the tab_once/tab_many
        # condition
        return autocomplete(line, self.position, self.filesystem, "all")


def autocomplete(line, position, filesystem, config):
    '''
    :params line: the line typed on the command line so far
    :type line: str
    :params position: path
    :type position: str
    :params filesystem: FileSystem object
    :params config: "all", "files", "dirs"
    '''
    completions = []

    if not line:
        # Add slash after all directories
        directories = filesystem.get_dirnames_at_path(position)
        directories = [d + "/" for d in directories]
        files = []

        if config == "all":
            files = filesystem.get_filenames_at_path(position)

        completions = directories + files
    else:
        final_text = line.split("/")[-1]
        complete_path = "/".join(line.split("/")[:-1])
        path = os.path.join(
            position, complete_path
        )
        exists, f = filesystem.path_exists(path)
        if exists and f.type == "directory":
            for child in f.children:
                if child.name.startswith(final_text):
                    if child.type == "directory":
                        completions.append(child.name + "/")
                    elif config == "all":
                        completions.append(child.name)

    return sorted(completions)
