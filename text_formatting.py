import tkinter

class TextFormatter:

    def __init__(self, conf):
        self._conf = conf # configuration passed from main application

        # This is needed when converting formatted text to normal text,
        # it contains a list of where in the formatted text bold markers should be inserted.
        self._bold_tag_indexes = []

        #This list contains indexes to point to start and end position of bold text
        self._bold_markers_indexes = [] #list of positon markers where bold tags are to be placed

        # This is needed when converting formatted text to normal text,
        # it contains a list of where in the formatted text 'title' markers should be inserted.
        self._title_tag_indexes = []

        #This list contains indexes to point to start and end position of 'title' text
        #self._title_markers_indexes = [] #list of positon markers where 'title' tags are to be placed



    #----------------------------------------------------
    # Look for  words/phrases surrounded by '**'
    # Set bold text and remove '**'
    #----------------------------------------------------
    def set_bold_text(self, text_widget):
        self._bold_tag_indexes = []
        self._bold_markers_indexes = []
        pos = "1.0"
        while pos != "":
            pos = text_widget.search("**",pos,'end-1c')
            if pos != "":
                #delete the '**'
                row,col = pos.split('.',1)
                col_int = int(col)+2
                text_widget.delete(pos,f"{row}.{str(col_int)}")
                self._bold_tag_indexes.append(pos) # save the index

        if len(self._bold_tag_indexes) % 2 != 0:
            self._bold_tag_indexes.pop() # remove last element as there is not a matching one

        font_name = self._conf.read_section('note window','text font name')
        font_size = self._conf.read_section('note window','text font size')
        font_type = ('bold')
        text_font = (font_name,int(font_size),font_type)
        #print(text_font)
        #How can we get the font as a tuple ??????????????

        text_widget.tag_configure("boldtext",font=text_font)

        mod=0
        last_row=None
        for index in range(0,len(self._bold_tag_indexes)-1,2):
            text_widget.tag_add("boldtext",self._bold_tag_indexes[index],self._bold_tag_indexes[index+1])
            #now modify marker index to be able to insert back in '**' later
            row, col = self._bold_tag_indexes[index].split('.',1)
            if last_row == None:
                last_row = row
            elif row != last_row:
                #the modifier need to be reset for a new row
                #print("resetting mod for new row")
                mod=0

            # this get a bit complicated as we have to adjust the indexes
            # as the characters get inserted.
            col1_int = int(col)+mod
            row, col = self._bold_tag_indexes[index+1].split('.',1)
            col2_int = int(col)+2+mod
            self._bold_markers_indexes.append(f"{row}.{str(col1_int)}")
            self._bold_markers_indexes.append(f"{row}.{str(col2_int)}")
            mod+=4


    #----------------------------------------------------
    # Look for  words/phrases starting with '##'
    # Set title text and remove '##'
    # Tile is per line. Only use thefirst '##' found in
    # the current line.
    #----------------------------------------------------
    def set_title_text(self, text_widget):
        self._title_tag_indexes = []
        #self._title_markers_indexes = []
        pos = "1.0"
        last_row_matched = '0'

        #get indexes for title text and remove the tag markers for titile texy  - '##'
        while pos != "":
            pos = text_widget.search("##",pos,'end-1c')
            if pos != "":
                #delete the '**'
                print("Found title")
                print(pos)
                row,col = pos.split('.',1)
                col_int = int(col)+2
                if last_row_matched != row: # only one title per line
                    last_row_matched = row
                    text_widget.delete(pos,f"{row}.{str(col_int)}")
                    self._title_tag_indexes.append(pos) # save the index

        #get font and configure tag
        font_name = self._conf.read_section('note window','title font name')
        font_size = self._conf.read_section('note window','title font size')
        font_type = ('bold')
        text_font = (font_name,int(font_size),font_type)
        text_widget.tag_configure("titletext",font=text_font)

        #now apply the title formmatting to the text widget
        for index in range(0,len(self._title_tag_indexes)):
            # apply the formatting tag to the text
            text_widget.tag_add("titletext",self._title_tag_indexes[index],f"{self._title_tag_indexes[index]} lineend")



    #--------------------------------------------------------------
    # Remove bold tags and title tags. Insert '**' back at start
    # and end of bold text
    #--------------------------------------------------------------
    def set_normal_text(self, text_widget):

        #remove bold text tags
        text_widget.tag_remove("boldtext",'1.0', 'end-1c')
        text_widget.tag_remove("titletext",'1.0', 'end-1c')

        #insert '##' back in
        for index in range(0,len(self._title_tag_indexes)):
            text_widget.insert(self._title_tag_indexes[index],"##")

             #insert back in '**'
        for index in range(0,len(self._bold_markers_indexes)-1,2):
            text_widget.insert(self._bold_markers_indexes[index],"**")
            text_widget.insert(self._bold_markers_indexes[index+1],"**")



