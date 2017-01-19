from ts3plugin import ts3plugin
import ts3, ts3defines, os.path, binascii, re, shutil
from os import path
from base64 import b64encode
from PythonQt.QtGui import QFileDialog

class Avatargrabber(ts3plugin):
    name = "Avatargrabber"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Luemmel"
    description = "Grab avatars."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Grab Avatar", "")]

    dlg = None
    destination = None

    def __init__(self):
        ts3.printMessageToCurrentTab("Avatargrabber by Luemmel - Thank you for using me!")

    def stop(self):
        pass

    def onMenuItemEvent(self, schid, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            if menu_item_id == 0:
                self.grab_avatar(schid, selected_item_id)

    def grab_avatar(self, schid, clientID):
        # convert uid to base64 uid
        (error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        suid = suid.encode('ascii')
        suid = b64encode(suid).decode("ascii")

        #check if client has avatar
        (error, avatarflag) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
        if avatarflag != "":
            (error, clientUID) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            clientUID = clientUID.split('=')[0]
            binary = ""
            for i in range(0, len(clientUID)):
                character = ord(clientUID[i])
                # a-z   26  51
                if 97 <= character <= 122: character -= 71
                # A-Z   0   25
                elif 65 <= character <= 90: character -= 65
                # 0-9   52  61
                elif 48 <= character <= 57: character += 4
                # +     62
                elif character == 43: character += 19
                # /     63
                elif character == 47: character += 16
                binary += '{0:06b}'.format(character)
            #convert to 6bit array
            binary = re.findall('....?', binary)

            filename = "avatar_"

            #convert 6bit to a-p
            for bits in binary: filename += chr(int(bits, 2)+97)

            # get paths and copy
            directory = path.join(ts3.getConfigPath(), "cache", suid, "clients", filename)
            self.open_dlg()
            if self.destination != "": shutil.copy2(directory, self.destination+"\\"+filename+".gif")

    def open_dlg(self):
        if not self.dlg: self.dlg = SettingsDialog(self)
        return True

class SettingsDialog(QFileDialog):
    def __init__(self, main, parent=None):
        main.destination = self.getExistingDirectory(self, "Open a folder", os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
