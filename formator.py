from gi.repository import GObject, Gedit, Gtk

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="EditMenu" action="Edit">
      <placeholder name="EditOps_7">
        <separator/>
        <menuitem name="RegexpAction" action="FormatorAction"/>
      </placeholder>
    </menu>
</menubar>
</ui>"""

class FormatorPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "Formator"
    window = GObject.property(type=Gedit.Window)
    
    def __init__(self):
        GObject.Object.__init__(self)

    def _add_ui(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("FormatorActions")
        self._actions.add_actions([
            ('FormatorAction', Gtk.STOCK_INFO, "Format Code", 
                None, "Format your code", 
                self.on_format_action_activate),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()

    def do_activate(self):
		self._add_ui()

    def do_deactivate(self):
        self._remove_ui()

    def do_update_state(self):
        pass
        
    def on_format_action_activate(self, action, data=None):
        view = self.window.get_active_view()
        if view:
            buf = view.get_buffer()
            start = buf.get_start_iter()
            end = buf.get_end_iter()
            text = buf.get_text(start, end, False);
            style = 'long'
            space_count = 4
            i = 0
            new_text = ""
            clean = False
            un_clean_char = ""
            current_spaces = 0
            old_spaces = 0
            new_line = True
            tag_start = False
            start_code = False;
            level = 1
            for char in text:
                if((char=='\'' or char=='"' or char == '`')and(text[i-1]!='\\')):
                    if(clean==False):
                        un_clean_char = char
                        clean = True
                    else:
                        clean = False
                    new_text=new_text+char
                    new_line = False
                elif(clean == True):
                    new_text=new_text+char
                elif(char=="\n"):
                    pass
                elif(char=='<'):
                    if(text[i+1]=='/'):
                        tag_start = False
                        if(text[i-1]!=' ' and text[i-2]!=' '):
                            new_text = new_text[0:-space_count]
                        current_spaces = current_spaces-space_count
                    elif(text[i+1]=='?' and text[i+2]=='p' and text[i+3]=='h' and text[i+4]=='p'):
                        old_spaces = current_spaces
                        start_code = True
                        current_spacs = 0
                    elif(text[i+1]=='!'):
                        old_spaces = current_spaces
                        current_spacs = 0
                    else:
                        tag_start = True
                        current_spaces = current_spaces+space_count
                    new_text=new_text+char
                elif(char=='>'):
                    if(text[i-1]=='/'):
                        current_spaces = current_spaces-space_count
                        new_text = new_text+char+'\n' + (' ' * current_spaces )
                        tag_start = False
                    elif(text[i-1]=='?'):
                        start_code = False
                        new_text=new_text+char+'\n' + (' ' * current_spaces)
                    elif(text[i-1]!='?'):
                        if(start_code==False):
                            if(tag_start==True):
                                new_text=new_text+char+'\n' + (' ' * current_spaces)
                            else:
                                new_text=new_text+char+'\n' + (' ' * current_spaces )
                        else:
                            print 'format'
                            new_text=new_text+char
                        #print tag_start
                        #print current_spaces
                    else:
                        new_text = new_text[0:-space_count]
                        current_spaces = current_spaces-space_count;
                        new_text = new_text+'?'+char+'\n' + (' ' * current_spaces )
                    new_line = True
                elif(char==';'):
                        new_text=new_text + ';\n' + (' ' * current_spaces)
                        new_line = True
                elif(char==' ' or char == '\t'):
                    if(char==' ' and text[i-1]!=' ' and new_line == False):
                        new_text = new_text + ' '
                elif(char=='{'):
                    if(text[i+1]=='}'):
                        new_text = new_text + char
                    else:
                        new_line = True
                        current_spaces = current_spaces+space_count
                        if(style=='long'):
                            new_text = new_text + '\n' + (' ' * (current_spaces-space_count)) + '{\n' +(' ' * current_spaces)
                        else:
                            new_text = new_text + '{\n' + (' ' * current_spaces)
                elif(char=='}'):
                    if(text[i-1]=='{'):
                        if(len(text)> (i+1) and text[i+1]==';'):
                            new_text = new_text + char
                        else:
                            new_text = new_text + '}\n' + (' ' * current_spaces)
                    else:
                        if(new_line == False):
                            print char
                            current_spaces = current_spaces-space_count
                            new_text = new_text + '\n' + (' ' * current_spaces) + '}\n' + (' ' * current_spaces)
                        else:
                            if(current_spaces>=space_count):
                                new_text = new_text[0:-space_count]
                            current_spaces = current_spaces-space_count
                            new_text = new_text + '}\n' + (' ' * current_spaces)
                        new_line = True
                elif(char == '='):
                    new_line = False
                    if(text[i-1]=='?' and text[i-2] == '<'):
                        new_text=new_text+char
                    else:
                        if(text[i-1]!=' '):
                            char = ' ' + char
                        if(text[i+1]!=' '):
                            char = char + ' '
                        new_text = new_text + char
                elif(char==','):
                    new_line = False
                    new_text = new_text+', '
                else:
                    new_line = False
                    new_text=new_text+char
                i=i+1
            print new_text
            buf.set_text(new_text)
    def get_spaces(self):
        pass
    def check_next_char(self, char, text, position, count=1):
        pass
    def check_prev_char(self, char, text, count=1):
        pass
    def _remove_ui(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()
