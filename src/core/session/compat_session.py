"""Backwards compatible session loader.

This module loads a omega session file which
have been generated by old omega versions
which uses different format.

"""
# pylint: disable=no-self-use
# pylint: disable=invalid-name

import copy
import pickle

from core import encoding


def rename_key(dictionnary, old_keyname, new_keyname):
    """If `old_keyname` exists in `dictionnary`, rename
    the key to `new_keyname`

    """
    if old_keyname in dictionnary:
        dictionnary[new_keyname] = dictionnary.pop(old_keyname)


def remove_key(dictionnary, keyname):
    """Remove `keyname` from `dictionnary` if it exists.

    """
    if keyname in dictionnary.keys():
        del dictionnary[keyname]


# pylint: disable=too-few-public-methods
class AbstractSessionLoader:
    """Abstract class for loading session files
    which have been generated by a deprecated
    omega framework version.

    """
    # empty raw session template (const)
    _template = {"Conf": {},
                 "Env": {},
                 "Alias": {},
                 "Cache": {},
                 "Hist": {},
                 "Compat": {},
                 "File": None
                }

    def __init__(self):
        pass

    def __call__(self, session_path):
        """Get raw session object from `session_path`.
        """
        new_session = copy.deepcopy(self._template)
        session_keys = new_session.keys()
        old_session = self._load_file(session_path)
        for attribute in dir(self):
            if attribute.startswith("set_"):
                target = attribute[4:].capitalize()
                if target not in session_keys:
                    raise ValueError("Invalid attribute: %r" % attribute)
                function = getattr(self, attribute)
                new_session[target] = function(old_session)
        return new_session

    def _load_file(self, session_path):
        """default file loader
        """
        with open(session_path, 'rb') as file:
            return pickle.load(file,
                               encoding=encoding.default_encoding,
                               errors=encoding.default_errors)


class Loader_V1_x(AbstractSessionLoader):
    """Load session file from omega <= v1.x
    """
    def set_conf(self, old_session):
        """Conf object setter"""
        result = old_session["SETTINGS"]

        # $EDITOR
        rename_key(result, "TEXTEDITOR", "EDITOR")

        # $HTTP_USER_AGENT
        rename_key(result, "USERAGENT", "HTTP_USER_AGENT")
        if result["HTTP_USER_AGENT"] == "%%RAND_UA%%":
            result["HTTP_USER_AGENT"] = "%%DEFAULT%%"

        # $PASSKEY
        remove_key(result, "POSTVAR")
        # rename_key(result, "POSTVAR", "PASSKEY")
        # if "%%HASHKEY%%" in result["PASSKEY"]:
        #     value = result["PASSKEY"]
        #     result["PASSKEY"] = value.replace("%%HASHKEY%%",
        #                                       old_session["ENV_HASH"])

        # $BACKDOOR
        remove_key(result, "BACKDOOR")
        # if "%%POSTVAR%%" in result["BACKDOOR"]:
        #     value = result["BACKDOOR"]
        #     if "'%%POSTVAR%%'" in value or '"%%POSTVAR%%"' in value:
        #         value = value.replace("%%POSTVAR%%", "%%PASSKEY%%")
        #     else:
        #         value = value.replace("%%POSTVAR%%", "'%%PASSKEY%%'")
        #     result["BACKDOOR"] = value

        # $TARGET
        if "OPENER" in old_session.keys():
            if "URL" in old_session["OPENER"].keys():
                result["TARGET"] = old_session["OPENER"]["URL"]

        return result

    def set_compat(self, old_session):
        """Compat object setter"""
        result = {}
        # Compat $id
        result["id"] = "v1"

        # Compat $passkey
        passkey = old_session["SETTINGS"]["POSTVAR"]
        if "%%HASHKEY%%" in passkey:
            result["passkey"] = passkey.replace("%%HASHKEY%%",
                                                old_session["ENV_HASH"])
        else:
            result["passkey"] = passkey

        return result

    def set_env(self, old_session):
        """Env object setter"""
        result = old_session["ENV"]

        rename_key(result, "CWD", "PWD")
        rename_key(result, "WRITE_TMPDIR", "WRITEABLE_TMPDIR")
        rename_key(result, "WRITE_WEBDIR", "WRITEABLE_WEBDIR")

        remove_key(result, "TEXTEDITOR")

        # Add some environment variables from old "SERVER" object.
        result["ADDR"] = old_session["SERVER"]["addr"]
        result["HOME"] = old_session["SERVER"]["home"]
        result["HOST"] = old_session["SERVER"]["host"]
        result["PHP_VERSION"] = old_session["SERVER"]["phpver"]
        result["PATH_SEP"] = old_session["SERVER"]["separator"]
        result["HTTP_SOFTWARE"] = old_session["SERVER"]["soft"]
        result["USER"] = old_session["SERVER"]["user"]
        result["PORT"] = old_session["SERVER"]["port"]
        result["CLIENT_ADDR"] = old_session["SERVER"]["client_addr"]

        # $PLATFORM
        result["PLATFORM"] = old_session["SERVER"]["os"].split()[0].lower()
        if result["PLATFORM"] in ["unknow", "unknown", ""]:
            if result["PATH_SEP"] == "\\":
                result["PLATFORM"] = "windows"
            else:
                result["PLATFORM"] = "unix"

        return result


class Loader_V2_1_4(AbstractSessionLoader):
    """Load session file from omega <= 2.1.4

    """
    def _load_file(self, session_path):
        """load file & check PSCOREVER"""
        old_session = super()._load_file(session_path)
        if int(old_session["PSCOREVER"]) != 2:
            raise ValueError("PSCOREVER must be 2")
        return old_session

    def set_conf(self, old_session):
        """Conf object setter"""
        result = old_session["SET"]

        # $EDITOR
        rename_key(result, "TEXTEDITOR", "EDITOR")

        # $BROWSER
        rename_key(result, "WEBBROWSER", "BROWSER")

        # $HTTP_USER_AGENT
        if "HTTP_USER_AGENT" in result.keys():
            old_defaults = ["file://misc/http/User-Agent.lst",
                            "file://framework/misc/http_user_agents.lst"]
            if result["HTTP_USER_AGENT"] in old_defaults:
                del result["HTTP_USER_AGENT"]

        # $SAVEFILE
        remove_key(result, "SAVEFILE")

        return result

    def set_env(self, old_session):
        """Env object setter"""
        result = old_session["ENV"]

        rename_key(result, "CWD", "PWD")
        rename_key(result, "WRITE_TMPDIR", "WRITEABLE_TMPDIR")
        rename_key(result, "WRITE_WEBDIR", "WRITEABLE_WEBDIR")

        remove_key(result, "TEXTEDITOR")

        # Add some environment variables from old "SRV" object.
        result["ADDR"] = old_session["SRV"]["addr"]
        result["HOME"] = old_session["SRV"]["home"]
        result["HOST"] = old_session["SRV"]["host"]
        result["PHP_VERSION"] = old_session["SRV"]["phpver"]
        result["PATH_SEP"] = old_session["SRV"]["separator"]
        result["HTTP_SOFTWARE"] = old_session["SRV"]["soft"]
        result["USER"] = old_session["SRV"]["user"]
        result["WEB_ROOT"] = old_session["SRV"]["webroot"]
        result["PORT"] = old_session["SRV"]["port"]
        result["CLIENT_ADDR"] = old_session["SRV"]["client_addr"]

        # $PLATFORM
        result["PLATFORM"] = old_session["SRV"]["os"].split()[0].lower()
        if result["PLATFORM"] in ["unknow", "unknown", ""]:
            if result["PATH_SEP"] == "\\":
                result["PLATFORM"] = "windows"
            else:
                result["PLATFORM"] = "unix"

        return result


def load(session_path):
    """Successively try to load session file
    with the list of compat session loaders.

    The list `compat_loaders` must be sorted starting
    with most recent loader
    """
    compat_loaders = [Loader_V2_1_4(), Loader_V1_x()]

    for old_session_load in compat_loaders:
        try:
            return old_session_load(session_path)
        except BaseException:
            pass