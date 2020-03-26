"""
Test module.
Tests the functions
in module `chatette.cli.interactive_commands.command_strategy`.
"""

import re
import pytest

from chatette.facade import Facade
from chatette.cli.interactive_commands.command_strategy import CommandStrategy
from chatette.cli.terminal_writer import RedirectionType
from chatette.utils import UnitType


def get_facade():
    if not Facade.was_instantiated():
        facade = \
            Facade(
                "tests/unit-testing/cli/interactive_commands/toilets.chatette",
                "tests/unit-testing/cli/interactive_commands/", None, False,
                None
            )
        facade.run_parsing()
    return Facade.get_or_create()

def new_facade():
    if Facade.was_instantiated():
        print("reset facade")
        facade = \
            Facade.reset_system(
                "tests/unit-testing/cli/interactive_commands/toilets.chatette",
                "tests/unit-testing/cli/interactive_commands/", None, False,
                None
            )
    else:
        print("new facade")
        facade = \
            Facade(
                "tests/unit-testing/cli/interactive_commands/toilets.chatette",
                "tests/unit-testing/cli/interactive_commands/", None, False,
                None
            )
    facade.run_parsing()
    return Facade.get_or_create()


class TestTokenize(object):
    def test_empty(self):
        assert CommandStrategy.tokenize("") == []

    def test_short_commands(self):
        assert CommandStrategy.tokenize("exit") == ["exit"]
        assert CommandStrategy.tokenize("stats  ") == ["stats"]
        assert CommandStrategy.tokenize("NOT-command") == ["NOT-command"]
        assert CommandStrategy.tokenize("NOT COMMAND") == ["NOT", "COMMAND"]
        assert CommandStrategy.tokenize('word "a name"') == ["word", '"a name"']
        assert CommandStrategy.tokenize(' open "quote a') == ["open", '"quote a']
        assert CommandStrategy.tokenize("regex /with space/i") == ["regex", "/with space/i"]

    def test_long_commands(self):
        assert CommandStrategy.tokenize('rule "~[a rule] tested"') == \
               ["rule", '"~[a rule] tested"']
        assert \
            CommandStrategy.tokenize(
                'set-modifier alias "something else" casegen "True"\t'
            ) == [
                "set-modifier", "alias",
                '"something else"', "casegen", '"True"'
            ]

    def test_escapement(self):
        assert CommandStrategy.tokenize('test "escaped \\" was here"') == \
               ["test", '"escaped \\" was here"']


class TestIsEndRegex(object):
    def test_empty(self):
        assert not CommandStrategy._is_end_regex("")
    
    def test_not_regex(self):
        assert not CommandStrategy._is_end_regex("test")
        assert not CommandStrategy._is_end_regex("something")
        assert not CommandStrategy._is_end_regex("a longer thing")
        assert not CommandStrategy._is_end_regex("/special characters$^")
    
    def test_regexes(self):
        assert CommandStrategy._is_end_regex("/something.*/")
        assert CommandStrategy._is_end_regex("/something else/i")
        assert CommandStrategy._is_end_regex("another /g")
        assert CommandStrategy._is_end_regex("/a last thing/ig")


class TestFindRedirectionFilePath(object):
    @staticmethod
    def to_tokens(text):
        return CommandStrategy.tokenize(text)

    def test_empty(self):
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("")) is None

    def test_no_redirection(self):
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("exit")) is None
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("test something")) is None
        assert CommandStrategy.find_redirection_file_path(self.to_tokens(
                    'long command "with quotes\" inside"'
               )) is None

    def test_truncate_redirection(self):
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("stats > test.txt")) == \
               (RedirectionType.truncate, "test.txt")
        assert CommandStrategy.find_redirection_file_path(self.to_tokens(
                    "another rule > different/path.extension"
               )) == (RedirectionType.truncate, "different/path.extension")
        assert CommandStrategy.find_redirection_file_path(self.to_tokens(
                    'rule "with quotes\" and escapements" > /path/no/extension'
               )) == (RedirectionType.truncate, "/path/no/extension")

    def test_append_redirection(self):
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("stats >> file.cc")) == \
               (RedirectionType.append, "file.cc")
        assert CommandStrategy.find_redirection_file_path(self.to_tokens(
                    "a command >> small/path.ext"
               )) == (RedirectionType.append, "small/path.ext")

    def test_quiet(self):
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("stats >>")) == \
               (RedirectionType.quiet, None)
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("exit >")) == \
               (RedirectionType.quiet, None)
        assert CommandStrategy.find_redirection_file_path(self.to_tokens("command >  ")) == \
               (RedirectionType.quiet, None)


class TestGetUnitTypeFromStr(object):
    def test_wrong_str(self):
        assert CommandStrategy.get_unit_type_from_str("") is None
        assert CommandStrategy.get_unit_type_from_str("t") is None
        assert CommandStrategy.get_unit_type_from_str("test") is None
        assert CommandStrategy.get_unit_type_from_str("SOMETHING") is None
        assert CommandStrategy.get_unit_type_from_str("\t\t ") is None
        assert CommandStrategy.get_unit_type_from_str("@%~") is None

    def test_correct_str(self):
        assert CommandStrategy.get_unit_type_from_str("alias") == UnitType.alias
        assert CommandStrategy.get_unit_type_from_str("AliaS") == UnitType.alias
        assert CommandStrategy.get_unit_type_from_str('~') == UnitType.alias
        assert CommandStrategy.get_unit_type_from_str("slot") == UnitType.slot
        assert CommandStrategy.get_unit_type_from_str("SLOT") == UnitType.slot
        assert CommandStrategy.get_unit_type_from_str('@') == UnitType.slot
        assert CommandStrategy.get_unit_type_from_str("intent") == UnitType.intent
        assert CommandStrategy.get_unit_type_from_str("iNtENt") == UnitType.intent
        assert CommandStrategy.get_unit_type_from_str('%') == UnitType.intent


class TestRemoveQuotes(object):
    def test(self):
        assert CommandStrategy.remove_quotes('"quoted"') == "quoted"
        assert CommandStrategy.remove_quotes('"the quotes"') == "the quotes"
        assert CommandStrategy.remove_quotes(r'"escaped\""') == 'escaped"'

class TestSplitExactUnitName(object):
    def test(self):
        assert CommandStrategy.split_exact_unit_name('"quoted"') == \
               ["quoted", None]
        assert CommandStrategy.split_exact_unit_name('"the quotes"') == \
               ["the quotes", None]
        assert CommandStrategy.split_exact_unit_name(r'"escaped\""') == \
               ['escaped"', None]
        assert CommandStrategy.split_exact_unit_name('"test#var"') == \
               ["test", "var"]
        assert CommandStrategy.split_exact_unit_name(r'"unit\#hashtag#var"') == \
               ["unit#hashtag", "var"]


class TestGetRegexName(object):
    def test_empty_command(self):
        assert CommandStrategy("").get_regex_name("") is None

    def test_no_regex(self):
        assert CommandStrategy("").get_regex_name("exit") is None
        assert CommandStrategy("").get_regex_name('"alias"') is None
        assert CommandStrategy("").get_regex_name('"something with/slash"') \
               is None

    def test_regex(self):
        assert CommandStrategy("").get_regex_name("/regex/") == \
               re.compile("regex")
        assert CommandStrategy("").get_regex_name("/test.*/") == \
               re.compile("test.*")
        assert CommandStrategy("").get_regex_name("/some[0-9]/i") == \
               re.compile("some[0-9]", re.IGNORECASE)
        obj = CommandStrategy("")
        assert obj.get_regex_name("/test/g") == re.compile("test")
        assert obj._is_regex_global
        obj = CommandStrategy("")
        assert obj.get_regex_name("/$x+^/ig") == re.compile("$x+^", re.IGNORECASE)
        assert obj._is_regex_global


class TestNextMatchingUnitName(object):
    pass # TODO

class TestGetAllMatchingUnitNames(object):
    pass # TODO


class TestRemoveRedirectionTokens(object):
    def test_redirection(self):
        obj = CommandStrategy("exit > path/to/file.txt")
        assert obj.command_tokens == ["exit"]
        obj = CommandStrategy('exist intent "test" >> file/no/extension')
        assert obj.command_tokens == ["exist", "intent", '"test"']
        obj = CommandStrategy("test something /else/i  > ")
        assert obj.command_tokens == ["test", "something", "/else/i"]


class TestFlushOutput(object):
    # NOTE: for coverage
    def test_flush(self):
        CommandStrategy("").flush_output()


class TestShouldExit(object):
    def test(self):
        assert not CommandStrategy("").should_exit()


class TestExecute(object):
    # NOTE: for coverage
    def test(self):
        with pytest.raises(NotImplementedError):
            CommandStrategy("NOTHING alias a, b, c").execute()


class TestExecuteOnUnit(object):
    def test_should_be_overriden(self):
        with pytest.raises(NotImplementedError):
            CommandStrategy("").execute_on_unit(None, None, None)


class TestFinishExecution(object):
    # NOTE: for coverage
    def test(self):
        CommandStrategy("").finish_execution()
